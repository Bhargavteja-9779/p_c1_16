#!/usr/bin/env python3
"""plan_v3 job: generalised factorial transport (hospital x control factor), feature-group and size variants.

Re-uses the FROZEN model code of src/train_eval.py (fit_lgbm, fit_lr, metrics) unchanged; only the cell
definition, the feature subset, the training-set size and pooled training differ.

Control factors (patient level, fixed in plan_v3 before any v3 result was seen):
  unit  : MICU / SICU (as in E1-E6; patients with unknown unit excluded)
  age   : Y = Age < 65, O = Age >= 65 (all patients)
  route : D = ICU admission within 24 h of hospital admission (HospAdmTime >= -24), L = later (all patients;
          the single patient with missing HospAdmTime is excluded)
Cells are "<hospital>_<level>", e.g. A_O. Four cells per factor.

Feature sets ("featset"):
  all      : value + trend + process + context (as E1)
  vitals   : vital-sign values + vital trends + context
  labs     : lab values + context
  noproc   : all minus process features
  proc     : process features + context
Size ("size"): full | matched (each source cell's train patients subsampled to the smallest train cell of that
  factor, stratified by sepsis status, sample seed = model seed).
Training cell may be pooled: "A_SICU+B_MICU" (union of the two cells' train / val splits).

Writes results/v3/<job_id>.json and results/v3/preds/<job_id>.npz (same layout as train_eval) and appends to
results/v3/raw_results_v3.csv. Idempotent.
"""
import argparse, csv, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.train_eval import fit_lgbm, fit_lr, metrics  # frozen code, unchanged
from src.data_physionet2019 import VITALS, LABS

LEVELS = {"unit": ("MICU", "SICU"), "age": ("Y", "O"), "route": ("D", "L")}


def cells_of(factor):
    return [f"{h}_{l}" for h in "AB" for l in LEVELS[factor]]


def load(factor):
    feat = pd.read_parquet(ROOT / "data/processed/features_v1.parquet")
    groups = json.loads((ROOT / "data/processed/features_v1.groups.json").read_text())
    sp = pd.read_csv(ROOT / "data/processed/splits_v1.csv", dtype={"pid": str})
    feat = feat.merge(sp[["pid", "split"]], on="pid", how="left")
    if factor == "unit":
        pu = feat[feat.unit != "UNK"].groupby("pid").unit.first()
        lvl = feat.pid.map(pu)
    elif factor == "age":
        a = feat.groupby("pid").Age.first()
        lvl = feat.pid.map(pd.Series(np.where(a >= 65, "O", "Y"), index=a.index))
    else:
        t = feat.groupby("pid").HospAdmTime.first()
        s = pd.Series(np.where(t.isna(), None, np.where(t >= -24, "D", "L")), index=t.index)
        lvl = feat.pid.map(s)
    feat["cell"] = feat.hospital + "_" + lvl.astype(object).where(lvl.notna(), "UNK").astype(str)
    feat = feat[feat.cell.isin(cells_of(factor))].reset_index(drop=True)
    return feat, groups


def featcols(groups, featset):
    v, t, p, c = groups["value"], groups["trend"], groups["process"], groups["context"]
    isvit = lambda col: col.split("_")[0] in VITALS
    islab = lambda col: col.rsplit("_", 1)[0] in LABS
    return {"all": v + t + p + c,
            "vitals": [x for x in v if isvit(x)] + t + c,
            "labs": [x for x in v if islab(x)] + c,
            "noproc": v + t + c,
            "proc": p + c}[featset]


def subsample(tr, n_pat, seed):
    pat = tr.groupby("pid").y.max()
    rng = np.random.default_rng(seed)
    keep = []
    for s, ids in pat.groupby(pat).groups.items():
        k = int(round(n_pat * len(ids) / len(pat)))
        keep += list(rng.choice(np.array(sorted(ids)), k, replace=False))
    return tr[tr.pid.isin(set(keep))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-id", required=True); ap.add_argument("--factor", choices=list(LEVELS), required=True)
    ap.add_argument("--train-cell", required=True); ap.add_argument("--model", choices=["lgbm", "lr"], required=True)
    ap.add_argument("--seed", type=int, required=True); ap.add_argument("--eval-split", choices=["val", "test"], required=True)
    ap.add_argument("--featset", default="all"); ap.add_argument("--size", choices=["full", "matched"], default="full")
    ap.add_argument("--experiment", required=True)
    a = ap.parse_args()
    outdir = ROOT / "results" / "v3"
    rf = outdir / f"{a.job_id}.json"
    if rf.exists():
        print("exists", rf); return
    t0 = time.time()
    feat, groups = load(a.factor)
    cols = featcols(groups, a.featset)
    tcs = a.train_cell.split("+")
    tr = feat[feat.cell.isin(tcs) & (feat.split == "train")]
    va = feat[feat.cell.isin(tcs) & (feat.split == "val")]
    if a.size == "matched":
        nmin = min(feat[(feat.cell == c) & (feat.split == "train")].pid.nunique() for c in cells_of(a.factor))
        tr = subsample(tr, nmin, a.seed)
    predict, sel = (fit_lgbm if a.model == "lgbm" else fit_lr)(tr, va, cols, a.seed)
    res = dict(job_id=a.job_id, experiment=a.experiment, factor=a.factor, train_cell=a.train_cell, model=a.model,
               seed=a.seed, eval_split=a.eval_split, featset=a.featset, size=a.size, n_features=len(cols),
               n_train_pat=int(tr.pid.nunique()), selection=sel, eval={})
    preds = {}
    for c in cells_of(a.factor):
        ev = feat[(feat.cell == c) & (feat.split == a.eval_split)]
        p = predict(ev)
        res["eval"][c] = metrics(ev.y.values, p, ev.pid.values)
        preds[f"{c}__pid"], preds[f"{c}__y"], preds[f"{c}__p"] = np.asarray(ev.pid.values, dtype="U12"), ev.y.values.astype(np.int8), p.astype(np.float32)
    res["seconds"] = round(time.time() - t0, 1)
    (outdir / "preds").mkdir(parents=True, exist_ok=True)
    np.savez_compressed(outdir / "preds" / f"{a.job_id}.npz", **preds)
    raw = outdir / "raw_results_v3.csv"
    new = not raw.exists()
    with open(raw, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["job_id", "experiment", "factor", "model", "featset", "size", "seed", "eval_split", "train_cell", "eval_cell", "auroc", "auprc", "pat_auroc"])
        for c, m in res["eval"].items():
            w.writerow([a.job_id, a.experiment, a.factor, a.model, a.featset, a.size, a.seed, a.eval_split, a.train_cell, c,
                        f"{m['auroc']:.5f}", f"{m['auprc']:.5f}", f"{m['pat_auroc']:.5f}"])
    tmp = rf.with_suffix(".tmp"); tmp.write_text(json.dumps(res, indent=1)); tmp.replace(rf)
    print(json.dumps({c: round(m["auroc"], 3) for c, m in res["eval"].items()}), sel, res["seconds"], "s")


if __name__ == "__main__":
    main()
