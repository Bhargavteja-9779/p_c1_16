#!/usr/bin/env python3
"""One job = train one model on one training cell, evaluate on all cells. Idempotent.

Cells: hospital x ICU unit (A_MICU, A_SICU, B_MICU, B_SICU); patients with unknown unit are excluded.
Training uses the cell's train split; model selection (early stopping / small grid) uses the cell's val split.
Evaluation split: 'val' (exploration) or 'test' (confirmation, frozen config only).

Writes results/<job_id>.json, results/preds/<job_id>.npz (per eval cell: pid, y, p) and appends rows to
results/raw_results.csv. Hour-level and patient-level (max risk) metrics.

Usage: python -m src.train_eval --job-id ID --train-cell A_MICU --model lgbm --seed 100 --eval-split val
         [--fixes none|harm|harm_noproc|harm_noproc_norm] [--quick]
"""
import argparse, csv, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import stats as S

CELLS = ["A_MICU", "A_SICU", "B_MICU", "B_SICU"]
LGBM_BASE = dict(objective="binary", learning_rate=0.05, min_child_samples=100, feature_fraction=0.8,
                 bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0, num_threads=int(os.environ.get("OMP_NUM_THREADS", 2)), verbose=-1)
LGBM_GRID = [15, 63, 255]          # num_leaves; 3 configs, chosen on source-cell val AUROC
LR_GRID = [0.01, 0.1, 1.0]         # C; 3 configs, same tuning budget as LightGBM


def load_cells(fixes):
    harm = fixes != "none"
    feat = pd.read_parquet(ROOT / "data/processed" / ("features_harm_v1.parquet" if harm else "features_v1.parquet"))
    groups = json.loads((ROOT / "data/processed/features_v1.groups.json").read_text())
    sp = pd.read_csv(ROOT / "data/processed/splits_v1.csv", dtype={"pid": str})
    feat = feat.merge(sp[["pid", "split"]], on="pid", how="left")
    pu = feat[feat.unit != "UNK"].groupby("pid").unit.first()
    feat["cell"] = feat.hospital + "_" + feat.pid.map(pu).fillna("UNK")
    feat = feat[feat.cell.isin(CELLS)].reset_index(drop=True)
    cols = groups["value"] + groups["trend"] + groups["process"] + groups["context"]
    if harm:
        cols = [c for c in cols if not c.startswith("EtCO2")]
    if fixes in ("harm_noproc", "harm_noproc_norm"):
        cols = [c for c in cols if c not in groups["process"]]
    if fixes == "harm_noproc_norm":  # per-hospital quantile normalisation fitted on unlabelled train rows
        for h in "AB":
            m = feat.hospital == h
            ref = feat.loc[m & (feat.split == "train")]
            for c in cols:
                r = np.sort(ref[c].dropna().values)
                if len(r) == 0:
                    continue
                x = feat.loc[m, c].values
                q = (np.searchsorted(r, x, "left") + np.searchsorted(r, x, "right")) / (2 * len(r))
                feat.loc[m, c] = np.where(np.isnan(x), np.nan, q).astype(np.float32)
    return feat, cols


def fit_lgbm(tr, va, cols, seed):
    import lightgbm as lgb
    best = None
    for nl in LGBM_GRID:
        dtr = lgb.Dataset(tr[cols], tr.y)
        m = lgb.train({**LGBM_BASE, "num_leaves": nl, "seed": seed}, dtr, 3000,
                      valid_sets=[lgb.Dataset(va[cols], va.y, reference=dtr)],
                      callbacks=[lgb.early_stopping(100, verbose=False)])
        a = S.auroc(va.y, m.predict(va[cols], num_iteration=m.best_iteration))
        if best is None or a > best[0]:
            best = (a, nl, m)
    a, nl, m = best
    return (lambda d: m.predict(d[cols], num_iteration=m.best_iteration)), dict(num_leaves=nl, best_iter=int(m.best_iteration), val_auroc=a)


def fit_lr(tr, va, cols, seed):
    from sklearn.linear_model import LogisticRegression
    med = tr[cols].median()
    lo, hi = tr[cols].quantile(0.005), tr[cols].quantile(0.995)

    def X(d):
        x = d[cols].clip(lo, hi, axis=1)
        ind = x.isna().astype(np.float32).values
        x = x.fillna(med).fillna(0).values.astype(np.float32)
        return x, ind
    xt, it = X(tr)
    mu, sd = xt.mean(0), xt.std(0) + 1e-6
    keep = it.std(0) > 0
    mk = lambda d: (lambda x, i: np.hstack([(x - mu) / sd, i[:, keep]]))(*X(d))
    Xtr, Xva = mk(tr), mk(va)
    best = None
    for C in LR_GRID:
        m = LogisticRegression(C=C, max_iter=300, random_state=seed).fit(Xtr, tr.y)
        a = S.auroc(va.y, m.predict_proba(Xva)[:, 1])
        if best is None or a > best[0]:
            best = (a, C, m)
    a, C, m = best
    return (lambda d: m.predict_proba(mk(d))[:, 1]), dict(C=C, val_auroc=a)


def metrics(y, p, pid):
    a, b, citl = S.calibration_slope_intercept(y, p)
    d = pd.DataFrame({"pid": pid, "y": y, "p": p}).groupby("pid").max()
    return dict(n_rows=int(len(y)), n_pat=int(len(d)), prev=float(np.mean(y)), auroc=S.auroc(y, p), auprc=S.auprc(y, p),
                brier=S.brier(y, p), cal_slope=b, citl=citl, pat_auroc=S.auroc(d.y, d.p), pat_auprc=S.auprc(d.y, d.p))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job-id", required=True); ap.add_argument("--train-cell", required=True)
    ap.add_argument("--model", choices=["lgbm", "lr"], required=True); ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--eval-split", choices=["val", "test"], required=True)
    ap.add_argument("--fixes", default="none"); ap.add_argument("--experiment", default="E1"); ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    outdir = ROOT / "results" / ("quick" if a.quick else "")
    rf = outdir / f"{a.job_id}.json"
    if rf.exists():
        print("exists", rf); return
    t0 = time.time()
    feat, cols = load_cells(a.fixes)
    if a.quick:  # 15% of patients, fixed
        pids = feat.pid.drop_duplicates().sample(frac=0.15, random_state=0)
        feat = feat[feat.pid.isin(pids)]
    tr = feat[(feat.cell == a.train_cell) & (feat.split == "train")]
    va = feat[(feat.cell == a.train_cell) & (feat.split == "val")]
    predict, sel = (fit_lgbm if a.model == "lgbm" else fit_lr)(tr, va, cols, a.seed)
    res = dict(job_id=a.job_id, experiment=a.experiment, train_cell=a.train_cell, model=a.model, seed=a.seed,
               eval_split=a.eval_split, fixes=a.fixes, n_features=len(cols), selection=sel, eval={})
    preds = {}
    for c in CELLS:
        ev = feat[(feat.cell == c) & (feat.split == a.eval_split)]
        p = predict(ev)
        res["eval"][c] = metrics(ev.y.values, p, ev.pid.values)
        preds[f"{c}__pid"], preds[f"{c}__y"], preds[f"{c}__p"] = np.asarray(ev.pid.values, dtype="U12"), ev.y.values.astype(np.int8), p.astype(np.float32)
    res["seconds"] = round(time.time() - t0, 1)
    (outdir / "preds").mkdir(parents=True, exist_ok=True)
    np.savez_compressed(outdir / "preds" / f"{a.job_id}.npz", **preds)
    raw = outdir / "raw_results.csv"
    new = not raw.exists()
    with open(raw, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["job_id", "experiment", "model", "fixes", "seed", "eval_split", "train_cell", "eval_cell", "auroc", "auprc", "pat_auroc", "cal_slope", "citl"])
        for c, m in res["eval"].items():
            w.writerow([a.job_id, a.experiment, a.model, a.fixes, a.seed, a.eval_split, a.train_cell, c,
                        f"{m['auroc']:.5f}", f"{m['auprc']:.5f}", f"{m['pat_auroc']:.5f}", f"{m['cal_slope']:.4f}", f"{m['citl']:.4f}"])
    tmp = rf.with_suffix(".tmp"); tmp.write_text(json.dumps(res, indent=1)); tmp.replace(rf)
    print(json.dumps({c: round(m["auroc"], 3) for c, m in res["eval"].items()}), sel, res["seconds"], "s")


if __name__ == "__main__":
    main()
