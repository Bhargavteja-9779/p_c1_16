#!/usr/bin/env python3
"""plan_v3 analysis (H4, H5, H6, E10). Re-uses the frozen bootstrap of scripts/analyze_transport.py unchanged
(patient-cluster bootstrap within target cell, same resample for all prediction sets, mean over seeds and cells).

  H4: D = AUROC_t(same-hospital other-level src) - AUROC_t(other-hospital same-level src), factors age / route,
      models lgbm / lr.                                     (4 tests)
  H5: D_all - D_vitals > 0 (unit factor, LightGBM; D_all from E1_explore (val) / E6_confirm (test)).   (1 test)
      D for labs / noproc / proc reported (estimates).
  H6: D > 0 with size-matched training, lgbm / lr.           (2 tests)
  Holm across the 7 tests.  E10: pooled (other-unit same hospital + same-unit other hospital) minus unit-src
      AUROC, estimate + CI (not in the family).
  Context: domain-classifier AUC (LightGBM, train rows -> val rows) for each control-factor pair vs site pair.

Usage: python3 scripts/analyze_v3.py --phase explore|confirm [--nboot 1000]
"""
import argparse, glob, json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
import analyze_transport as AT  # frozen functions
from src.train_eval_v3 import cells_of, LEVELS, load, featcols

OTHER_H = {"A": "B", "B": "A"}


def set_factor(f):
    lv = LEVELS[f]
    AT.CELLS = cells_of(f)
    def src_of(t):
        h, l = t.split("_"); o = lv[1] if l == lv[0] else lv[0]
        return {"local": t, "unit": f"{h}_{o}", "site": f"{OTHER_H[h]}_{l}", "both": f"{OTHER_H[h]}_{o}"}
    AT.src_of = src_of


def load_v3(exp, factor, model, featset, size, split):
    out = {}
    for f in glob.glob(str(ROOT / f"results/v3/preds/{exp}__{factor}__{model}__{featset}__{size}__*__{split}.npz")):
        parts = Path(f).stem.split("__")
        out.setdefault(int(parts[6][1:]), {})[parts[5]] = dict(np.load(f))
    return out


def summ(vals_point, vals_boot):
    pt = float(vals_point); bs = np.asarray(vals_boot)
    lo, hi = np.percentile(bs, [2.5, 97.5]); p = min(1.0, 2 * min((bs <= 0).mean(), (bs >= 0).mean()))
    return dict(estimate=pt, ci95=[float(lo), float(hi)], p_boot=float(max(p, 1 / len(bs))), nboot=int(len(bs)))


def meanD(point_or_boot, key="D"):
    return float(np.mean([point_or_boot[t][key] for t in AT.CELLS]))


def holm(ps):
    k = sorted(ps, key=ps.get); m = len(k); out = {}; run = 0
    for i, n in enumerate(k):
        run = max(run, min(1.0, (m - i) * ps[n])); out[n] = run
    return out


def domain_auc(factor, pairs):
    import lightgbm as lgb
    from sklearn.metrics import roc_auc_score
    feat, groups = load(factor); cols = featcols(groups, "all"); res = {}
    for a, b in pairs:
        d = feat[feat.cell.isin([a, b])]
        tr, va = d[d.split == "train"], d[d.split == "val"]
        m = lgb.train(dict(objective="binary", num_leaves=31, learning_rate=0.1, verbose=-1, num_threads=2, seed=0),
                      lgb.Dataset(tr[cols], (tr.cell == b).astype(int)), 200)
        res[f"{a} vs {b}"] = float(roc_auc_score((va.cell == b).astype(int), m.predict(va[cols])))
    return res


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--phase", choices=["explore", "confirm"], required=True)
    ap.add_argument("--nboot", type=int, default=1000); ap.add_argument("--no-domain", action="store_true")
    a = ap.parse_args()
    sfx, split = ("x", "val") if a.phase == "explore" else ("c", "test")
    base_exp = "E1_explore" if a.phase == "explore" else "E6_confirm"
    rng = np.random.default_rng(20261125)
    R = {"phase": a.phase, "split": split, "nboot": a.nboot, "tests": {}, "estimates": {}, "per_cell": {}}

    # H4: other control factors
    for f in ("age", "route"):
        set_factor(f)
        for model in ("lgbm", "lr"):
            P = load_v3(f"E7_factors{sfx}", f, model, "all", "full", split)
            pt, bs = AT.analyse(P, "hour", a.nboot, rng)
            ok = [b for b in bs if len(b) == 4]
            name = f"H4_{f}_{model}"
            R["tests"][name] = summ(meanD(pt), [meanD(b) for b in ok])
            R["estimates"][name] = {k: summ(meanD(pt, k), [meanD(b, k) for b in ok]) for k in ("gap_unit", "gap_site")}
            R["per_cell"][name] = {t: pt[t]["auroc"] for t in AT.CELLS}
            ptp, bsp = AT.analyse(P, "patient", max(200, a.nboot // 5), rng)
            okp = [b for b in bsp if len(b) == 4]
            R["estimates"][name + "_patient"] = summ(meanD(ptp), [meanD(b) for b in okp])

    # H5 mechanism + H6 size + E10 pooled (unit factor)
    set_factor("unit")
    Pall = AT.load_preds(base_exp, "lgbm", "none", split)
    Ps = {"all": Pall}
    for fs in ("vitals", "labs", "noproc", "proc"):
        Ps[fs] = load_v3(f"E8_mech{sfx}", "unit", "lgbm", fs, "full", split)
    pt, bs = AT.analyse_joint(Ps, "hour", a.nboot, rng)
    n = len(bs["all"]); ok = [i for i in range(n) if all(len(bs[k][i]) == 4 for k in Ps)]
    for k in Ps:
        R["estimates"][f"H5_D_{k}"] = summ(meanD(pt[k]), [meanD(bs[k][i]) for i in ok])
        R["estimates"][f"H5_gapsite_{k}"] = summ(meanD(pt[k], "gap_site"), [meanD(bs[k][i], "gap_site") for i in ok])
        R["estimates"][f"H5_gapunit_{k}"] = summ(meanD(pt[k], "gap_unit"), [meanD(bs[k][i], "gap_unit") for i in ok])
        R["per_cell"][f"H5_{k}"] = {t: pt[k][t]["auroc"] for t in AT.CELLS}
    R["tests"]["H5_Dall_minus_Dvitals"] = summ(meanD(pt["all"]) - meanD(pt["vitals"]),
                                               [meanD(bs["all"][i]) - meanD(bs["vitals"][i]) for i in ok])
    for model in ("lgbm", "lr"):
        P = load_v3(f"E9_size{sfx}", "unit", model, "all", "matched", split)
        p6, b6 = AT.analyse(P, "hour", a.nboot, rng); ok6 = [b for b in b6 if len(b) == 4]
        R["tests"][f"H6_matched_{model}"] = summ(meanD(p6), [meanD(b) for b in ok6])
        R["per_cell"][f"H6_{model}"] = {t: p6[t]["auroc"] for t in AT.CELLS}

    # E10 pooled: AUROC_t(pooled) - AUROC_t(unit-src) and - AUROC_t(site-src), via a pseudo role table
    Ppool = {}
    for f in glob.glob(str(ROOT / f"results/v3/preds/E10_pool{sfx}__unit__lgbm__all__full__*__{split}.npz")):
        parts = Path(f).stem.split("__"); u, s = parts[5].split("-")
        h = u.split("_")[0]; t = f"{h}_{s.split('_')[1]}"
        Ppool.setdefault(int(parts[6][1:]), {})[t] = dict(np.load(f))
    # build a prediction set where role 'local' is replaced by the pooled model for each target
    Pmix = {s: {**Pall[s]} for s in Ppool}
    saved_src = AT.src_of
    def src_pool(t):
        r = saved_src(t); r["local"] = f"POOL_{t}"; return r
    for s in Ppool:
        for t, z in Ppool[s].items():
            Pmix[s][f"POOL_{t}"] = z
    AT.src_of = src_pool
    pp, bp = AT.analyse(Pmix, "hour", a.nboot, rng); okp = [b for b in bp if len(b) == 4]
    AT.src_of = saved_src
    # gap_unit here = pooled - unit-src ... sign: gap_unit = AUROC(local=pooled) - AUROC(unit)
    R["estimates"]["E10_pooled_minus_unitsrc"] = summ(meanD(pp, "gap_unit"), [meanD(b, "gap_unit") for b in okp])
    R["estimates"]["E10_pooled_minus_sitesrc"] = summ(meanD(pp, "gap_site"), [meanD(b, "gap_site") for b in okp])
    R["per_cell"]["E10_pooled"] = {t: pp[t]["auroc"]["local"] for t in AT.CELLS}

    R["holm"] = holm({k: v["p_boot"] for k, v in R["tests"].items()})
    if not a.no_domain:
        R["domain_auc"] = {}
        for f in ("unit", "age", "route"):
            l0, l1 = LEVELS[f]
            R["domain_auc"][f] = domain_auc(f, [(f"A_{l0}", f"A_{l1}"), (f"B_{l0}", f"B_{l1}"), (f"A_{l0}", f"B_{l0}"), (f"A_{l1}", f"B_{l1}")])

    out = ROOT / f"results/analysis/v3_{a.phase}.json"
    out.write_text(json.dumps(R, indent=1))
    L = [f"# plan_v3 analysis — {a.phase} ({split}), nboot {a.nboot}\n", "## Confirmatory family (Holm)\n",
         "| test | estimate [95% CI] | p (boot) | p (Holm) |", "|---|---|---|---|"]
    for k, v in R["tests"].items():
        L.append(f"| {k} | {v['estimate']:.3f} [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}] | {v['p_boot']:.4f} | {R['holm'][k]:.4f} |")
    L += ["\n## Estimates\n", "| quantity | estimate [95% CI] |", "|---|---|"]
    for k, v in R["estimates"].items():
        if "estimate" in v:
            L.append(f"| {k} | {v['estimate']:.3f} [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}] |")
        else:
            for kk, vv in v.items():
                L.append(f"| {k}.{kk} | {vv['estimate']:.3f} [{vv['ci95'][0]:.3f}, {vv['ci95'][1]:.3f}] |")
    if "domain_auc" in R:
        L += ["\n## Domain-classifier AUC (shift size)\n", "| factor | pair | AUC |", "|---|---|---|"]
        for f, d in R["domain_auc"].items():
            for k, v in d.items():
                L.append(f"| {f} | {k} | {v:.3f} |")
    (ROOT / f"tables/v3_{a.phase}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
