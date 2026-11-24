#!/usr/bin/env python3
"""E5: how well can a receiving hospital know a transported model's AUROC before deployment?

For every off-diagonal transfer (source cell -> target cell) and model/seed in experiment EXP (split SPLIT):
  observed      = AUROC of the source model on the target cell (hour level)
  est_internal  = AUROC of the source model on its own cell (what the developer reports)
  est_implied   = label-free 'model-implied' AUROC on target predictions: sum_ij p_i(1-p_j)1[p_i>p_j] / sum_ij p_i(1-p_j)
                  (exact if the model were calibrated in the target)
  est_iw        = importance-weighted AUROC on the source cell; weights from a domain classifier (LightGBM, rows of
                  source-train vs target-train cell, all features, no labels), clipped at the 99th percentile
Few-label check (split-half, no finite-population optimism): target-cell patients are split at random into halves;
n labelled patients are drawn from half 1 (500 draws, new split each draw), the classical AUROC on their hours is compared
with the AUROC on the disjoint half 2. Reports P(|difference| <= 0.03) for n in N_GRID (conservative: includes the
reference half's own sampling noise).
H3: |error| > 0.03 in >= 50% of transfers, for each label-free estimator.
Usage: python3 scripts/e5_estimators.py --experiment E1_explore --split val
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from analyze_transport import load_preds, auc_fast, CELLS
from sklearn.metrics import roc_auc_score
N_GRID = [50, 100, 200, 400]


def implied_auc(p, max_n=20000, seed=0):
    p = np.asarray(p, float)
    if len(p) > max_n:
        p = np.random.default_rng(seed).choice(p, max_n, replace=False)
    o = np.sort(p)                       # sum over pairs i>j in score order: p_i * (1 - p_j)
    cum_neg = np.cumsum(1 - o) - (1 - o)  # sum_{j<i} (1-p_j)
    num = np.sum(o * cum_neg)
    den = o.sum() * (1 - o).sum() - np.sum(o * (1 - o))
    return float(num / den)


def domain_weights(src, tgt, split):
    import lightgbm as lgb
    from src.train_eval import load_cells
    feat, cols = load_cells("none")
    tr = feat[feat.split == "train"]; X = pd.concat([tr[tr.cell == src][cols], tr[tr.cell == tgt][cols]])
    d = np.r_[np.zeros((tr.cell == src).sum()), np.ones((tr.cell == tgt).sum())]
    m = lgb.train(dict(objective="binary", learning_rate=0.1, num_leaves=31, min_child_samples=100, num_threads=4, verbose=-1, seed=0),
                  lgb.Dataset(X, d), 200)
    ev = feat[(feat.cell == src) & (feat.split == split)]
    q = np.clip(m.predict(ev[cols]), 1e-4, 1 - 1e-4)
    w = q / (1 - q) * ((d == 0).sum() / (d == 1).sum())
    w = np.minimum(w, np.quantile(w, 0.99))
    dom_auc = roc_auc_score(np.r_[np.zeros(len(ev)), np.ones(((feat.cell == tgt) & (feat.split == split)).sum())],
                            np.r_[m.predict(ev[cols]), m.predict(feat[(feat.cell == tgt) & (feat.split == split)][cols])])
    return ev.pid.values.astype(str), w, float(dom_auc)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--experiment", default="E1_explore"); ap.add_argument("--split", default="val")
    a = ap.parse_args(); t0 = time.time(); rng = np.random.default_rng(7)
    W = {}
    for s in CELLS:
        for t in CELLS:
            if s != t:
                W[(s, t)] = domain_weights(s, t, a.split); print("domain", s, t, round(W[(s, t)][2], 4), flush=True)
    rows, few = [], []
    for model in ("lgbm", "lr"):
        P = load_preds(a.experiment, model, "none", a.split)
        for seed, byc in sorted(P.items()):
            for s in CELLS:
                z = byc[s]
                ys, ps = z[f"{s}__y"].astype(int), z[f"{s}__p"]
                internal = auc_fast(ys, ps)
                for t in CELLS:
                    if s == t: continue
                    yt, pt, pidt = z[f"{t}__y"].astype(int), z[f"{t}__p"], z[f"{t}__pid"].astype(str)
                    obs = auc_fast(yt, pt)
                    pid_s, w, dauc = W[(s, t)]
                    assert (pid_s == z[f"{s}__pid"].astype(str)).all()
                    iw = roc_auc_score(ys, ps, sample_weight=w)
                    kind = "site" if s[0] != t[0] and s[2:] == t[2:] else ("unit" if s[0] == t[0] else "both")
                    rows.append(dict(model=model, seed=seed, source=s, target=t, kind=kind, observed=obs, est_internal=internal,
                                     est_implied=implied_auc(pt), est_iw=iw, domain_auc=dauc, ess_frac=float(w.sum()**2 / (w**2).sum() / len(w))))
                    if seed == min(P) :
                        up = np.unique(pidt); idx_by = pd.Series(np.arange(len(pidt))).groupby(pidt).apply(np.array)
                        for n in N_GRID:
                            errs = []
                            for _ in range(500):
                                perm = rng.permutation(up); h1, h2 = perm[: len(up) // 2], perm[len(up) // 2:]
                                sel = rng.choice(h1, min(n, len(h1)), replace=False)
                                ii = np.concatenate(idx_by.loc[sel].values); jj = np.concatenate(idx_by.loc[h2].values)
                                if 0 < yt[ii].sum() < len(ii) and 0 < yt[jj].sum() < len(jj):
                                    errs.append(auc_fast(yt[ii], pt[ii]) - auc_fast(yt[jj], pt[jj]))
                            errs = np.array(errs)
                            few.append(dict(model=model, source=s, target=t, n_patients=n, draws_valid=len(errs),
                                            p_within_003=float((np.abs(errs) <= 0.03).mean()), sd=float(errs.std())))
    df = pd.DataFrame(rows); fw = pd.DataFrame(few)
    for e in ("est_internal", "est_implied", "est_iw"):
        df[f"err_{e[4:]}"] = df[e] - df.observed
    od = ROOT / "results/analysis"; od.mkdir(parents=True, exist_ok=True)
    df.to_csv(od / f"E5_{a.experiment}_{a.split}_estimators.csv", index=False); fw.to_csv(od / f"E5_{a.experiment}_{a.split}_fewlabel.csv", index=False)
    summ = {}
    for model, g in df.groupby("model"):
        summ[model] = {e: dict(mae=float(g[f"err_{e}"].abs().mean()), mean_err=float(g[f"err_{e}"].mean()),
                               frac_abs_gt_003=float((g[f"err_{e}"].abs() > 0.03).mean()), n=int(len(g))) for e in ("internal", "implied", "iw")}
        summ[model]["fewlabel_p_within_003_by_n"] = fw[fw.model == model].groupby("n_patients").p_within_003.mean().round(3).to_dict()
    (od / f"E5_{a.experiment}_{a.split}.json").write_text(json.dumps(summ, indent=1))
    L = [f"# E5 ({a.experiment}, {a.split}) — estimating transported AUROC (hour level)\n", "| model | estimator | MAE | mean error | share |err| > 0.03 | n transfers×seeds |", "|---|---|---|---|---|---|"]
    for m, v in summ.items():
        for e in ("internal", "implied", "iw"):
            L.append(f"| {m} | {e} | {v[e]['mae']:.3f} | {v[e]['mean_err']:+.3f} | {v[e]['frac_abs_gt_003']:.2f} | {v[e]['n']} |")
    L += ["\n## Few-label local check (split-half): P(|AUROC on n local patients − AUROC on disjoint half| ≤ 0.03), mean over 12 transfers\n", "| model | " + " | ".join(f"n={n}" for n in N_GRID) + " |", "|---|" + "---|" * len(N_GRID)]
    for m, v in summ.items():
        L.append(f"| {m} | " + " | ".join(f"{v['fewlabel_p_within_003_by_n'].get(n, float('nan')):.2f}" for n in N_GRID) + " |")
    (ROOT / "tables" / f"E5_{a.experiment}_{a.split}.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
    import importlib.util
    spec = importlib.util.spec_from_file_location("db", ROOT / "scripts/diagnose_baseline.py"); db = importlib.util.module_from_spec(spec); sys.argv = [sys.argv[0]]; spec.loader.exec_module(db)
    db.add_budget(time.time() - t0)


if __name__ == "__main__":
    main()
