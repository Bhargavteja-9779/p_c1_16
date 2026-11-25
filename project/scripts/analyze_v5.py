#!/usr/bin/env python3
"""plan_v5 / H8 dose-response analysis (written before any E12 result; see experiments/plan_v5.yaml).

Points (LightGBM, all features, hour-level AUROC, averaged over seeds):
  within-hospital transfer (h, a -> b):  gap = AUROC_hb(local hb) - AUROC_hb(model ha)
  cross-hospital transfer (h, a -> h', a): gap = AUROC_h'a(local h'a) - AUROC_h'a(model ha)
for 11 partitions: unit (E1_explore / E6_confirm preds), age, route (E7_factors), sex, age50, age75, route6, los,
rand1-3 (E12_dose).
Shift size S per (source cell, target cell): LightGBM domain classifier (train rows of both cells -> val rows), no
outcome labels. S_kl = symmetric KL estimate = mean logit on target val rows - mean logit on source val rows
(balanced class weights, probabilities clipped to [1e-6, 1-1e-6]); S_auc = domain AUC. Cached in
results/analysis/v5_shift.json (label-free, shared by both phases).
H8: residual R = mean_site [gap - (a + b S)], OLS fitted on within-hospital points; partition bootstrap.
H8-sens: S_auc; isotonic fit (extrapolated as constant beyond the largest within-hospital S).
H8b: mean site gap vs the largest partition-mean within-hospital gap.
Usage: python3 scripts/analyze_v5.py --phase explore|confirm [--nboot 2000]
"""
import argparse, glob, json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
from analyze_transport import auc_fast
from src.train_eval_v3 import load, featcols, cells_of, LEVELS

PARTS = ["unit", "age", "route", "sex", "age50", "age75", "route6", "los", "rand1", "rand2", "rand3"]
DEFVAR = {"age": "Age", "age50": "Age", "age75": "Age", "route": "HospAdmTime", "route6": "HospAdmTime", "sex": "Gender"}
OH = {"A": "B", "B": "A"}


def preds_for(f, phase):
    split = "val" if phase == "explore" else "test"; sfx = "x" if phase == "explore" else "c"
    if f == "unit":
        pat = f"results/preds/{'E1_explore' if phase == 'explore' else 'E6_confirm'}__lgbm__none__*__{split}.npz"
        key = lambda st: (int(st.split("__")[4][1:]), st.split("__")[3])
    else:
        exp = "E7_factors" if f in ("age", "route") else "E12_dose"
        pat = f"results/v3/preds/{exp}{sfx}__{f}__lgbm__all__full__*__{split}.npz"
        key = lambda st: (int(st.split("__")[6][1:]), st.split("__")[5])
    P = {}
    for fp in glob.glob(str(ROOT / pat)):
        s, c = key(Path(fp).stem); P.setdefault(s, {})[c] = dict(np.load(fp, allow_pickle=True))
    return P


def auc_matrix(P, cells):
    M = {}
    for tc in cells:
        for ec in cells:
            M[(tc, ec)] = float(np.mean([auc_fast(P[s][tc][f"{ec}__y"].astype(int), P[s][tc][f"{ec}__p"]) for s in P]))
    return M


def shift_sizes(recompute=False):
    out = ROOT / "results/analysis/v5_shift.json"
    S = json.loads(out.read_text()) if out.exists() else {}
    import lightgbm as lgb
    from sklearn.metrics import roc_auc_score
    for f in PARTS:
        if f in S and not recompute:
            continue
        feat, groups = load(f)
        cols = [c for c in featcols(groups, "all") if c != DEFVAR.get(f)]
        cells = cells_of(f); S[f] = {}
        pairs = [(a, b) for a in cells for b in cells if a < b and (a[0] == b[0] or a[2:] == b[2:])]
        for a, b in pairs:
            d = feat[feat.cell.isin([a, b])]
            tr, va = d[d.split == "train"], d[d.split == "val"]
            yt = (tr.cell == b).astype(int); w = np.where(yt == 1, 0.5 / yt.mean(), 0.5 / (1 - yt.mean()))
            m = lgb.train(dict(objective="binary", num_leaves=31, learning_rate=0.1, verbose=-1, num_threads=4, seed=0),
                          lgb.Dataset(tr[cols], yt, weight=w), 200)
            p = np.clip(m.predict(va[cols]), 1e-6, 1 - 1e-6); lg = np.log(p / (1 - p)); yv = (va.cell == b).values
            S[f][f"{a}|{b}"] = dict(kl=float(lg[yv].mean() - lg[~yv].mean()), auc=float(roc_auc_score(yv, p)))
            print(f, a, b, S[f][f"{a}|{b}"], flush=True)
        out.write_text(json.dumps(S, indent=1))
    return S


def points(phase, S):
    rows = []
    for f in PARTS:
        P = preds_for(f, phase)
        if not P:
            print("missing preds", f); continue
        cells = cells_of(f); M = auc_matrix(P, cells)
        for src in cells:
            for tgt in cells:
                if src == tgt:
                    continue
                same_h, same_l = src[0] == tgt[0], src[2:] == tgt[2:]
                if not (same_h or same_l):
                    continue
                k = f"{min(src, tgt)}|{max(src, tgt)}"
                rows.append(dict(part=f, src=src, tgt=tgt, kind="within" if same_h else "site",
                                 gap=M[(tgt, tgt)] - M[(src, tgt)], kl=S[f][k]["kl"], auc=S[f][k]["auc"]))
    return pd.DataFrame(rows)


def residual(df, parts, x, iso=False):
    w = df[df.part.isin(parts) & (df.kind == "within")]; s = df[df.part.isin(parts) & (df.kind == "site")]
    if iso:
        from sklearn.isotonic import IsotonicRegression
        ir = IsotonicRegression(out_of_bounds="clip").fit(w[x], w.gap)
        return float((s.gap - ir.predict(s[x])).mean())
    b, a = np.polyfit(w[x], w.gap, 1)
    return float((s.gap - (a + b * s[x])).mean())


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--phase", choices=["explore", "confirm"], required=True)
    ap.add_argument("--nboot", type=int, default=2000); a = ap.parse_args()
    S = shift_sizes(); df = points(a.phase, S)
    df.to_csv(ROOT / f"results/analysis/v5_points_{a.phase}.csv", index=False)
    rng = np.random.default_rng(20261125); parts = sorted(df.part.unique())
    R = {"phase": a.phase, "n_partitions": len(parts), "n_within": int((df.kind == "within").sum()), "n_site": int((df.kind == "site").sum())}
    specs = {"H8_kl_ols": ("kl", False), "H8sens_auc_ols": ("auc", False), "H8sens_kl_iso": ("kl", True), "H8sens_auc_iso": ("auc", True)}
    for name, (x, iso) in specs.items():
        est = residual(df, parts, x, iso); bs = []
        for _ in range(a.nboot):
            bp = list(rng.choice(parts, len(parts), replace=True))
            dd = pd.concat([df[df.part == p] for p in bp])
            try:
                bs.append(residual(dd, bp, x, iso))
            except Exception:
                pass
        bs = np.array(bs); lo, hi = np.percentile(bs, [2.5, 97.5]); p = min(1.0, 2 * min((bs <= 0).mean(), (bs >= 0).mean()))
        R[name] = dict(estimate=est, ci95=[float(lo), float(hi)], p_boot=float(max(p, 1 / len(bs))), nboot=int(len(bs)))
    pm = df[df.kind == "within"].groupby("part").gap.mean(); site_mean = float(df[df.kind == "site"].gap.mean())
    bprob = []
    for _ in range(a.nboot):
        bp = rng.choice(parts, len(parts), replace=True); dd = pd.concat([df[df.part == p] for p in bp])
        bprob.append(dd[dd.kind == "site"].gap.mean() > dd[dd.kind == "within"].groupby("part").gap.mean().max())
    R["H8b"] = dict(site_mean_gap=site_mean, max_within_partition=pm.idxmax(), max_within_gap=float(pm.max()),
                    holds=bool(site_mean > pm.max()), partition_bootstrap_prob=float(np.mean(bprob)))
    R["within_partition_mean_gap"] = pm.round(4).to_dict()
    R["site_partition_mean_gap"] = df[df.kind == "site"].groupby("part").gap.mean().round(4).to_dict()
    R["range"] = {k: {x: [float(df[df.kind == k][x].min()), float(df[df.kind == k][x].max())] for x in ("kl", "auc")} for k in ("within", "site")}
    w = df[df.kind == "within"]; R["within_fit_kl"] = dict(zip(("slope", "intercept"), map(float, np.polyfit(w.kl, w.gap, 1))))
    R["within_corr"] = {x: float(np.corrcoef(w[x], w.gap)[0, 1]) for x in ("kl", "auc")}
    (ROOT / f"results/analysis/v5_{a.phase}.json").write_text(json.dumps(R, indent=1))
    L = [f"# plan_v5 dose-response — {a.phase}\n", "| test | residual [95% CI] | p (boot) |", "|---|---|---|"]
    for k in specs:
        v = R[k]; L.append(f"| {k} | {v['estimate']:.3f} [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}] | {v['p_boot']:.4f} |")
    L += ["", f"H8b: mean site gap {site_mean:.3f} vs largest within-partition mean gap {pm.max():.3f} ({pm.idxmax()}); "
          f"holds={R['H8b']['holds']}; partition-bootstrap P = {R['H8b']['partition_bootstrap_prob']:.3f}", "",
          f"Shift-size ranges: {json.dumps(R['range'])}", f"Within-hospital corr(gap, S): {json.dumps(R['within_corr'])}", "",
          "| partition | within mean gap | site mean gap |", "|---|---|---|"]
    for p in parts:
        L.append(f"| {p} | {R['within_partition_mean_gap'].get(p, float('nan')):.3f} | {R['site_partition_mean_gap'].get(p, float('nan')):.3f} |")
    (ROOT / f"tables/v5_{a.phase}.md").write_text("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    main()
