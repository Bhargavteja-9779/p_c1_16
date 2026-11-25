#!/usr/bin/env python3
"""plan_v6 analysis (written before any v6 result; frozen before plan_v6b adds the confirm phase).

Task T2 (hypotension early warning), cells = {A,B,M} x {MICU,SICU}. For each seed, model and featset:
  AUC[t][s] = hour-level AUROC on target cell t's eval rows of the model trained on cell s.
  gap(s->t) = AUC[t][t] - AUC[t][s].
  W(t)  = the same-site other-unit source; X(t) = other-site same-unit sources (2); XX(t) = other-site other-unit (2).
  D9 = mean_t [ mean_{s in X(t)} gap(s->t) - gap(W(t)->t) ]        (H9, per model; Holm over 2 models)
  D_pair (H9b) = same, restricted to the X source from the paired site, over the target cells of the pair's two sites
  H9c = D9(all) - D9(noproc)   (lgbm; paired bootstrap)
  H10 = mean X-gap A<->M minus mean X-gap B<->M (descriptive)
Inference: cluster bootstrap over patients within each target cell (identical resample for every source model and
seed), AUROC averaged over seeds inside each replicate; percentile 95% CI; two-sided p = 2*min(P(D*<=0), P(D*>=0)).
Usage: python3 scripts/analyze_v6.py --phase explore|confirm [--nboot 2000]
Writes results/analysis/v6_<phase>.json and tables/v6_<phase>.md
"""
import argparse, glob, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
from analyze_transport import prep_auc, auc_w
from src import stats as S

CELLS = ["A_MICU", "A_SICU", "B_MICU", "B_SICU", "M_MICU", "M_SICU"]
SITES = ["A", "B", "M"]
site = lambda c: c.split("_")[0]
unit = lambda c: c.split("_")[1]
W = lambda t: [s for s in CELLS if site(s) == site(t) and unit(s) != unit(t)][0]
X = lambda t: [s for s in CELLS if site(s) != site(t) and unit(s) == unit(t)]


def load(exp, model, fs, split):
    P = {}
    for f in glob.glob(str(ROOT / f"results/v6/preds/{exp}__{model}__{fs}__*__{split}.npz")):
        p = Path(f).stem.split("__")
        P.setdefault(int(p[4][1:]), {})[p[3]] = dict(np.load(f))
    return P


def contrasts(AUC):
    """AUC: dict (t, s) -> value (already averaged over seeds). Returns all contrast statistics."""
    gap = {(s, t): AUC[(t, t)] - AUC[(t, s)] for t in CELLS for s in CELLS}
    out = {"D9": float(np.mean([np.mean([gap[(s, t)] for s in X(t)]) - gap[(W(t), t)] for t in CELLS])),
           "gap_W": float(np.mean([gap[(W(t), t)] for t in CELLS])),
           "gap_X": float(np.mean([gap[(s, t)] for t in CELLS for s in X(t)])),
           "gap_XX": float(np.mean([gap[(s, t)] for t in CELLS for s in CELLS if site(s) != site(t) and unit(s) != unit(t)]))}
    for a, b in (("A", "B"), ("A", "M"), ("B", "M")):
        ts = [t for t in CELLS if site(t) in (a, b)]
        oth = {a: b, b: a}
        out[f"D_{a}{b}"] = float(np.mean([gap[(f"{oth[site(t)]}_{unit(t)}", t)] - gap[(W(t), t)] for t in ts]))
        out[f"gapX_{a}{b}"] = float(np.mean([gap[(f"{oth[site(t)]}_{unit(t)}", t)] for t in ts]))
    out["H10"] = out["gapX_AM"] - out["gapX_BM"]
    out["gap"] = {f"{s}->{t}": float(v) for (s, t), v in gap.items()}
    return out


def point(P):
    seeds = sorted(P)
    AUC = {(t, s): float(np.mean([S.auroc(P[k][s][f"{t}__y"], P[k][s][f"{t}__p"]) for k in seeds])) for t in CELLS for s in CELLS}
    APR = {(t, s): float(np.mean([S.auprc(P[k][s][f"{t}__y"], P[k][s][f"{t}__p"]) for k in seeds])) for t in CELLS for s in CELLS}
    return AUC, APR


def boot(Ps, nboot, seed=0):
    """Ps: dict name -> P (same eval rows across names). Returns name -> list of contrast dicts per replicate."""
    rng = np.random.default_rng(seed)
    any_P = next(iter(Ps.values())); k0 = sorted(any_P)[0]
    pid = {t: any_P[k0][CELLS[0]][f"{t}__pid"] for t in CELLS}
    for name, P in Ps.items():  # all models must be evaluated on identical rows
        for k in P:
            for s in CELLS:
                for t in CELLS:
                    assert np.array_equal(P[k][s][f"{t}__pid"], pid[t]), (name, k, s, t)
    inv = {t: np.unique(pid[t], return_inverse=True) for t in CELLS}
    preps = {name: {(k, s, t): prep_auc(P[k][s][f"{t}__y"].astype(int), P[k][s][f"{t}__p"]) for k in P for s in CELLS for t in CELLS}
             for name, P in Ps.items()}
    res = {name: [] for name in Ps}
    for _ in range(nboot):
        w = {}
        for t in CELLS:
            u, iv = inv[t]
            cnt = np.bincount(rng.integers(0, len(u), len(u)), minlength=len(u)).astype(float)
            w[t] = cnt[iv]
        for name, P in Ps.items():
            AUC = {(t, s): float(np.mean([auc_w(preps[name][(k, s, t)], w[t]) for k in P])) for t in CELLS for s in CELLS}
            c = contrasts(AUC); c.pop("gap")
            res[name].append(c)
    return res


def summar(pt, reps, key):
    v = np.array([r[key] for r in reps])
    lo, hi = np.quantile(v, [0.025, 0.975])
    p = 2 * min((v <= 0).mean(), (v >= 0).mean())
    return dict(est=pt, lo=float(lo), hi=float(hi), p=float(max(p, 1 / len(v))))


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--phase", required=True); ap.add_argument("--nboot", type=int, default=500)
    a = ap.parse_args()
    exp_m, exp_x = ("E13_T2x", "E14_T2_mechx") if a.phase == "explore" else ("E13_T2c", "E14_T2_mechc")
    split = "val" if a.phase == "explore" else "test"
    Ps = {"lgbm_all": load(exp_m, "lgbm", "all", split), "lr_all": load(exp_m, "lr", "all", split),
          "lgbm_noproc": load(exp_x, "lgbm", "noproc", split), "lgbm_vitals": load(exp_x, "lgbm", "vitals", split)}
    Ps = {k: v for k, v in Ps.items() if v and all(len(v[s]) == 6 for s in v)}
    out = {"phase": a.phase, "nboot": a.nboot, "n_seeds": {k: len(v) for k, v in Ps.items()}, "point": {}, "tests": {}}
    pts = {}
    for name, P in Ps.items():
        AUC, APR = point(P)
        pts[name] = contrasts(AUC)
        out["point"][name] = {"contrasts": pts[name], "auc": {f"{s}->{t}": AUC[(t, s)] for t in CELLS for s in CELLS},
                              "auprc": {f"{s}->{t}": APR[(t, s)] for t in CELLS for s in CELLS}}
    B = boot(Ps, a.nboot)
    T = out["tests"]
    for m in ("lgbm_all", "lr_all"):
        if m in B:
            T[f"H9_{m}"] = summar(pts[m]["D9"], B[m], "D9")
            for pr in ("AB", "AM", "BM"):
                T[f"H9b_{pr}_{m}"] = summar(pts[m][f"D_{pr}"], B[m], f"D_{pr}")
            T[f"H10_{m}"] = summar(pts[m]["H10"], B[m], "H10")
    if "lgbm_noproc" in B and "lgbm_all" in B:
        diff = [x["D9"] - y["D9"] for x, y in zip(B["lgbm_all"], B["lgbm_noproc"])]
        T["H9c"] = summar(pts["lgbm_all"]["D9"] - pts["lgbm_noproc"]["D9"], [{"d": d} for d in diff], "d")
    for m in ("lgbm_noproc", "lgbm_vitals"):
        if m in B:
            T[f"D9_{m}"] = summar(pts[m]["D9"], B[m], "D9")
    fam9 = [k for k in T if k.startswith("H9_")]
    for k, h in zip(fam9, S.holm([T[k]["p"] for k in fam9])):
        T[k]["p_holm"] = h
    fam9b = [k for k in T if k.startswith("H9b_")]
    for k, h in zip(fam9b, S.holm([T[k]["p"] for k in fam9b])):
        T[k]["p_holm"] = h
    (ROOT / "results/analysis").mkdir(exist_ok=True)
    (ROOT / f"results/analysis/v6_{a.phase}.json").write_text(json.dumps(out, indent=1))
    L = [f"# plan_v6 {a.phase} (split {split}; nboot {a.nboot}; seeds {out['n_seeds']})", "",
         "| test | estimate | 95% CI | p | p (Holm) |", "|---|---|---|---|---|"]
    for k, v in T.items():
        L.append(f"| {k} | {v['est']:.4f} | [{v['lo']:.4f}, {v['hi']:.4f}] | {v['p']:.4f} | {v.get('p_holm', float('nan')):.4f} |")
    L += ["", "| model | gap W (same site, other unit) | gap X (other site, same unit) | gap XX | D_AB | D_AM | D_BM |", "|---|---|---|---|---|---|---|"]
    for name, c in pts.items():
        L.append(f"| {name} | {c['gap_W']:.4f} | {c['gap_X']:.4f} | {c['gap_XX']:.4f} | {c['D_AB']:.4f} | {c['D_AM']:.4f} | {c['D_BM']:.4f} |")
    L += ["", "AUROC matrix (rows = target cell, columns = training cell), lgbm_all:", "",
          "| target \\ source | " + " | ".join(CELLS) + " |", "|---" * 7 + "|"]
    if "lgbm_all" in out["point"]:
        au = out["point"]["lgbm_all"]["auc"]
        for t in CELLS:
            L.append(f"| {t} | " + " | ".join(f"{au[f'{s}->{t}']:.3f}" for s in CELLS) + " |")
    (ROOT / f"tables/v6_{a.phase}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
