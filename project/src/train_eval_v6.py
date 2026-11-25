#!/usr/bin/env python3
"""plan_v6 job: task T2 (hypotension early warning), 3 databases x 2 units. One job = one model trained on one
cell (train split; selection on the same cell's val split), evaluated on all 6 cells (val or test).
Reuses the frozen fit_lgbm / fit_lr / metrics from src/train_eval.py (same grids = same tuning budget).
Writes results/v6/<job_id>.json and results/v6/preds/<job_id>.npz. Idempotent.
Usage: python -m src.train_eval_v6 --job-id ID --train-cell A_MICU --model lgbm --featset all --seed 0 --eval-split val
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.train_eval import fit_lgbm, fit_lr, metrics

CELLS6 = ["A_MICU", "A_SICU", "B_MICU", "B_SICU", "M_MICU", "M_SICU"]
VITALS6 = ["HR", "Temp", "SBP", "MAP", "DBP", "Resp"]


def featcols6(groups, featset):
    v, t, p, c = groups["value"], groups["trend"], groups["process"], groups["context"]
    return {"all": v + t + p + c,
            "noproc": v + t + c,
            "vitals": [x for x in v if x.rsplit("_", 1)[0] in VITALS6] + t + c}[featset]


def main():
    ap = argparse.ArgumentParser()
    for k in ("--job-id", "--train-cell", "--model", "--featset", "--eval-split"):
        ap.add_argument(k, required=True)
    ap.add_argument("--seed", type=int, required=True); ap.add_argument("--experiment", default="E13_T2")
    a = ap.parse_args()
    out = ROOT / "results/v6"
    rf = out / f"{a.job_id}.json"
    if rf.exists():
        print("exists", rf); return
    t0 = time.time()
    feat = pd.read_parquet(ROOT / "data/processed/features_v6.parquet")
    groups = json.loads((ROOT / "data/processed/features_v6.groups.json").read_text())
    cols = featcols6(groups, a.featset)
    tr = feat[(feat.cell == a.train_cell) & (feat.split == "train")]
    va = feat[(feat.cell == a.train_cell) & (feat.split == "val")]
    predict, sel = (fit_lgbm if a.model == "lgbm" else fit_lr)(tr, va, cols, a.seed)
    res = dict(job_id=a.job_id, experiment=a.experiment, train_cell=a.train_cell, model=a.model, featset=a.featset,
               seed=a.seed, eval_split=a.eval_split, n_features=len(cols), selection=sel, eval={})
    preds = {}
    for c in CELLS6:
        ev = feat[(feat.cell == c) & (feat.split == a.eval_split)]
        p = predict(ev)
        res["eval"][c] = metrics(ev.y.values, p, ev.pid.values)
        preds[f"{c}__pid"] = np.asarray(ev.pid.values, dtype="U12")
        preds[f"{c}__y"], preds[f"{c}__p"] = ev.y.values.astype(np.int8), p.astype(np.float32)
    res["seconds"] = round(time.time() - t0, 1)
    (out / "preds").mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "preds" / f"{a.job_id}.npz", **preds)
    tmp = rf.with_suffix(".tmp"); tmp.write_text(json.dumps(res, indent=1)); tmp.replace(rf)
    print(json.dumps({c: round(m["auroc"], 3) for c, m in res["eval"].items()}), sel, res["seconds"], "s")


if __name__ == "__main__":
    main()
