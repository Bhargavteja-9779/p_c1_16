#!/usr/bin/env python3
"""H1/H2 analysis of the factorial transport experiment (frozen before E6; see plan_v1.yaml).

For target cell t (hospital h, unit u):
  local(t)  = model trained on t;  unit_src(t) = same hospital, other unit;  site_src(t) = other hospital, same unit
  gap_unit(t) = AUROC_t(local) - AUROC_t(unit_src);   gap_site(t) = AUROC_t(local) - AUROC_t(site_src)
  D(t) = gap_site - gap_unit = AUROC_t(unit_src) - AUROC_t(site_src)        (local model cancels)
H1: mean_t D > 0. Inference: patient-cluster bootstrap within each target cell (paired: same resampled patients
for all models), statistic averaged over seeds and the 4 target cells. Two-sided p = 2*min(P(D*<=0), P(D*>=0)).
H2: share of the site component removed by fix f = 1 - mean D_f / mean D_none (LightGBM), bootstrap CI.
Metric: hour-level AUROC (primary); patient-level AUROC (max risk) as secondary.

Usage: python3 scripts/analyze_transport.py --experiment E1_explore --split val [--fix-exp E2_fixes] [--nboot 1000]
Writes results/analysis/<experiment>_<split>.json and tables/<experiment>_<split>_*.md
"""
import argparse, glob, json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import rankdata
ROOT = Path(__file__).resolve().parents[1]
CELLS = ["A_MICU", "A_SICU", "B_MICU", "B_SICU"]
other_h = {"A": "B", "B": "A"}; other_u = {"MICU": "SICU", "SICU": "MICU"}


def src_of(t):
    h, u = t.split("_")
    return {"local": t, "unit": f"{h}_{other_u[u]}", "site": f"{other_h[h]}_{u}", "both": f"{other_h[h]}_{other_u[u]}"}


def auc_fast(y, p):
    r = rankdata(p); n1 = y.sum(); n0 = len(y) - n1
    return (r[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def prep_auc(y, p):
    """Precompute tie groups (sorted unique scores) once; weighted AUROC then costs two bincounts."""
    u, g = np.unique(p, return_inverse=True)
    return g, len(u), y.astype(bool)


def auc_w(prep, w):
    g, k, y = prep
    pos = np.bincount(g[y], weights=w[y], minlength=k); neg = np.bincount(g[~y], weights=w[~y], minlength=k)
    P, N = pos.sum(), neg.sum()
    below = np.cumsum(neg) - neg
    return float(np.sum(pos * (below + 0.5 * neg)) / (P * N))


def load_preds(exp, model, fixes, split):
    """returns {seed: {train_cell: npz}}"""
    out = {}
    for f in glob.glob(str(ROOT / f"results/preds/{exp}__{model}__{fixes}__*__{split}.npz")):
        parts = Path(f).stem.split("__")
        cell, seed = parts[3], int(parts[4][1:])
        out.setdefault(seed, {})[cell] = dict(np.load(f, allow_pickle=True))  # own files
    return out


def patient_level(pid, y, p):
    d = pd.DataFrame({"pid": pid, "y": y, "p": p}).groupby("pid", sort=True).max()
    return d.index.values, d.y.values, d.p.values


def cell_arrays(P, t, level):
    """For target t: y, patient index per row, and score arrays for each role & seed (aligned rows)."""
    seeds = sorted(P)
    any_ = P[seeds[0]][t]
    pid, y = any_[f"{t}__pid"], any_[f"{t}__y"].astype(int)
    roles = src_of(t)
    S = {r: [] for r in roles}
    for s in seeds:
        for r, c in roles.items():
            z = P[s][c]
            assert (z[f"{t}__pid"] == pid).all()
            S[r].append(z[f"{t}__p"])
    if level == "patient":
        S2 = {r: [] for r in roles}
        for r in roles:
            for v in S[r]:
                pp, yy, vv = patient_level(pid, y, v); S2[r].append(vv)
        pid, y, S = pp, yy, S2
    upid, inv = np.unique(pid, return_inverse=True)
    return y, inv, len(upid), {r: np.vstack(v) for r, v in S.items()}


def stat_from_aucs(a):
    return dict(auroc=a, gap_unit=a["local"] - a["unit"], gap_site=a["local"] - a["site"], gap_both=a["local"] - a["both"],
                D=a["unit"] - a["site"])


def analyse_joint(Ps, level, nboot, rng):
    """Ps: {name: preds}. Same patient resample (cluster bootstrap as integer weights) for every prediction set."""
    arrays = {n: {t: cell_arrays(P, t, level) for t in CELLS} for n, P in Ps.items()}
    ref = next(iter(arrays.values()))
    for n in arrays:
        for t in CELLS:
            assert len(arrays[n][t][0]) == len(ref[t][0]) and (arrays[n][t][1] == ref[t][1]).all(), "rows not aligned"
    preps = {n: {t: {r: [prep_auc(arrays[n][t][0], v) for v in V] for r, V in arrays[n][t][3].items()} for t in CELLS} for n in arrays}
    def stats(n, t, w):
        return stat_from_aucs({r: float(np.mean([auc_w(pp, w) for pp in L])) for r, L in preps[n][t].items()})
    point = {n: {t: stats(n, t, np.ones(len(ref[t][0]))) for t in CELLS} for n in arrays}
    boots = {n: [] for n in arrays}
    for b in range(nboot):
        ws = {}
        for t in CELLS:
            y, inv, npat, _ = ref[t]
            w = np.bincount(rng.integers(0, npat, npat), minlength=npat)[inv].astype(float)
            ws[t] = w if 0 < w[y == 1].sum() < w.sum() else None
        for n in arrays:
            boots[n].append({t: stats(n, t, ws[t]) for t in CELLS if ws[t] is not None})
    return point, boots


def analyse(P, level, nboot, rng):
    point, boots = analyse_joint({"x": P}, level, nboot, rng)
    return point["x"], boots["x"]


def summarise(point, boots, key):
    pt = np.mean([point[t][key] for t in CELLS])
    bs = np.array([np.mean([r[t][key] for t in CELLS]) for r in boots if len(r) == 4])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    p = min(1.0, 2 * min((bs <= 0).mean(), (bs >= 0).mean()))
    return dict(estimate=float(pt), ci95=[float(lo), float(hi)], p_boot=float(max(p, 1 / len(bs))), nboot=int(len(bs)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment", default="E1_explore"); ap.add_argument("--split", default="val")
    ap.add_argument("--fix-exp", default=None); ap.add_argument("--nboot", type=int, default=1000)
    a = ap.parse_args()
    rng = np.random.default_rng(20261124)
    out = {"experiment": a.experiment, "split": a.split, "H1": {}, "H2": {}, "cells": {}}
    pts = {}
    for model in ("lgbm", "lr"):
        P = load_preds(a.experiment, model, "none", a.split)
        if not P or any(len(v) < 4 for v in P.values()):
            print("incomplete", model, {s: len(v) for s, v in P.items()}); continue
        for level in ("hour", "patient"):
            point, boots = analyse(P, level, a.nboot if level == "hour" else max(200, a.nboot // 5), rng)
            k = f"{model}_{level}"
            out["H1"][k] = {m: summarise(point, boots, m) for m in ("D", "gap_site", "gap_unit", "gap_both")}
            out["H1"][k]["ratio_site_over_unit"] = out["H1"][k]["gap_site"]["estimate"] / out["H1"][k]["gap_unit"]["estimate"]
            out["H1"][k]["seeds"] = sorted(P)
            out["cells"][k] = point
    fix_exp = a.fix_exp or a.experiment
    Ps = {"none": load_preds(a.experiment, "lgbm", "none", a.split)}
    for fixes in ("harm", "harm_noproc", "harm_noproc_norm"):
        P = load_preds(fix_exp, "lgbm", fixes, a.split)
        if P and all(len(v) == 4 for v in P.values()) and sorted(P) == sorted(Ps["none"]):
            Ps[fixes] = P
    if len(Ps) > 1:
        point, boots = analyse_joint(Ps, "hour", a.nboot, rng)   # paired: same patients for all fix variants
        mD = lambda rec: np.mean([rec[t]["D"] for t in CELLS])
        D0 = mD(point["none"])
        for fixes in [k for k in Ps if k != "none"]:
            Df = mD(point[fixes])
            share = np.array([1 - mD(bf) / mD(b0) for b0, bf in zip(boots["none"], boots[fixes]) if len(b0) == 4 and len(bf) == 4])
            diff = np.array([mD(b0) - mD(bf) for b0, bf in zip(boots["none"], boots[fixes]) if len(b0) == 4 and len(bf) == 4])
            out["H2"][fixes] = dict(D_none=float(D0), D_fix=float(Df), share_removed=float(1 - Df / D0),
                                    share_ci95=[float(x) for x in np.percentile(share, [2.5, 97.5])],
                                    p_share_lt_half=float(max((share >= 0.5).mean(), 1 / len(share))),
                                    D_reduction=float(D0 - Df), D_reduction_ci95=[float(x) for x in np.percentile(diff, [2.5, 97.5])],
                                    p_reduction=float(max(min(1.0, 2 * min((diff <= 0).mean(), (diff >= 0).mean())), 1 / len(diff))),
                                    gap_site=float(np.mean([point[fixes][t]["gap_site"] for t in CELLS])),
                                    gap_unit=float(np.mean([point[fixes][t]["gap_unit"] for t in CELLS])), seeds=sorted(Ps[fixes]))
            out["cells"][f"lgbm_hour_{fixes}"] = point[fixes]
    fam = {}
    for k in ("lgbm_hour", "lr_hour"):
        if k in out["H1"]: fam[f"H1_{k}"] = out["H1"][k]["D"]["p_boot"]
    if "harm_noproc_norm" in out["H2"]: fam["H2_reduction"] = out["H2"]["harm_noproc_norm"]["p_reduction"]
    if fam:
        ks = sorted(fam, key=fam.get); m = len(ks); adj = {}; run = 0
        for i, k in enumerate(ks):
            run = max(run, min(1.0, (m - i) * fam[k])); adj[k] = run
        out["holm"] = {k: dict(p=fam[k], p_holm=adj[k]) for k in fam}
    od = ROOT / "results/analysis"; od.mkdir(parents=True, exist_ok=True)
    (od / f"{a.experiment}_{a.split}.json").write_text(json.dumps(out, indent=1, default=float))
    td = ROOT / "tables"; td.mkdir(exist_ok=True)
    L = [f"# {a.experiment} ({a.split}) — transport gaps (AUROC; gap = local − transported; mean of 4 target cells)\n",
         "| model/level | gap_unit [95% CI] | gap_site [95% CI] | D = site − unit [95% CI] | p (boot) | site/unit ratio |", "|---|---|---|---|---|---|"]
    f3 = lambda s: f"{s['estimate']:.3f} [{s['ci95'][0]:.3f}, {s['ci95'][1]:.3f}]"
    for k, v in out["H1"].items():
        L.append(f"| {k} | {f3(v['gap_unit'])} | {f3(v['gap_site'])} | {f3(v['D'])} | {v['D']['p_boot']:.4f} | {v['ratio_site_over_unit']:.2f} |")
    if out["H2"]:
        L += ["\n## Unlabelled site fixes (LightGBM, hour level)\n", "| fixes | D (site − unit) | share of site component removed [95% CI] | P(share ≥ 0.5) | gap_site | gap_unit |", "|---|---|---|---|---|---|"]
        L.append(f"| none | {out['H2'][next(iter(out['H2']))]['D_none']:.3f} | — | — | — | — |")
        for f, v in out["H2"].items():
            L.append(f"| {f} | {v['D_fix']:.3f} | {v['share_removed']:.2f} [{v['share_ci95'][0]:.2f}, {v['share_ci95'][1]:.2f}] | {v['p_share_lt_half']:.3f} | {v['gap_site']:.3f} | {v['gap_unit']:.3f} |")
    L += ["\n## Per target cell (hour-level AUROC by source role)\n", "| model | target | local | unit-src | site-src | both | D |", "|---|---|---|---|---|---|---|"]
    for k, cells in out["cells"].items():
        if "patient" in k: continue
        for t, v in cells.items():
            A = v["auroc"]; L.append(f"| {k} | {t} | {A['local']:.3f} | {A['unit']:.3f} | {A['site']:.3f} | {A['both']:.3f} | {v['D']:.3f} |")
    if out.get("holm"):
        L += ["\n## Holm-corrected family\n", "| test | p (boot) | p (Holm) |", "|---|---|---|"] + [f"| {k} | {v['p']:.4f} | {v['p_holm']:.4f} |" for k, v in out["holm"].items()]
    (td / f"{a.experiment}_{a.split}_transport.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
