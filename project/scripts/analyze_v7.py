#!/usr/bin/env python3
"""plan_v7 analysis (written before v7 results except one exploration smoke job; frozen before plan_v7b).

For task T in {T1, T2}: transfers s->t (W same site / X other site same unit / XX other site other unit).
AUROC per (transfer, seed, n, method) on target eval rows; averaged over seeds, then over transfers of a type.
H12: X transfers, n = primary_n: SPRU - best baseline (best baseline fixed from exploration and stored in
     results/analysis/v7_best_baseline.json; at confirmation it is read, never recomputed). Holm over tasks.
H13: SPRU - resid_phys and SPRU - resid_rand (X, n = primary_n); Holm over 4.
H14: [SPRU - source](X) - [SPRU - source](W), n = primary_n (CI only).
Inference: cluster bootstrap over patients within each target cell (identical weights for all sources, seeds and
methods evaluated on that target), percentile CI, two-sided p = 2 min(P(<=0), P(>=0)).
Usage: python3 scripts/analyze_v7.py --phase explore|confirm [--nboot 2000]
"""
import argparse, glob, json, sys
from pathlib import Path
import numpy as np
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
from analyze_transport import prep_auc, auc_w
from src import stats as S

NS = [50, 100, 200, 400]; PRIMARY = 100
BASELINES = ["source", "local", "pooled", "resid_all"]
METHODS = BASELINES + ["spru", "resid_phys", "resid_rand"]


def ttype(s, t):
    if s.split("_")[0] == t.split("_")[0]:
        return "W"
    return "X" if s.split("_")[1] == t.split("_")[1] else "XX"


def load(task, phase):
    tag, split = ("v7x", "val") if phase == "explore" else ("v7c", "test")
    D = {}
    for f in glob.glob(str(ROOT / f"results/v7/preds/{tag}__{task}__*__{split}.npz")):
        p = Path(f).stem.split("__")
        D[(p[2], p[3], int(p[4][1:]))] = dict(np.load(f))
    return D


def key(n, m):
    return "source" if m == "source" else f"{n}__{m}"


def stats_from(aucf, D, n, typ):
    """mean over transfers of type typ of seed-mean AUROC, per method"""
    out = {}
    trs = sorted({(s, t) for (s, t, k) in D if ttype(s, t) == typ})
    for m in METHODS:
        out[m] = float(np.mean([np.mean([aucf(s, t, k, key(n, m)) for (s2, t2, k) in D if (s2, t2) == (s, t)]) for (s, t) in trs]))
    return out


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--phase", required=True); ap.add_argument("--nboot", type=int, default=500)
    a = ap.parse_args()
    bbf = ROOT / "results/analysis/v7_best_baseline.json"
    res = {"phase": a.phase, "nboot": a.nboot, "tasks": {}}
    tests = {}
    for task in ("T1", "T2"):
        D = load(task, a.phase)
        if not D:
            continue
        R = res["tasks"][task] = {"n_jobs": len(D), "curves": {}}
        pa = lambda s, t, k, kk: S.auroc(D[(s, t, k)]["y"], D[(s, t, k)][kk])
        for typ in ("W", "X", "XX"):
            for n in NS:
                R["curves"][f"{typ}_{n}"] = stats_from(pa, D, n, typ)
        cx = R["curves"][f"X_{PRIMARY}"]
        if a.phase == "explore":
            bb = json.loads(bbf.read_text()) if bbf.exists() else {}
            bb[task] = max(BASELINES, key=lambda m: cx[m]); bbf.write_text(json.dumps(bb, indent=1))
        best = json.loads(bbf.read_text())[task]
        R["best_baseline"] = best
        # bootstrap
        targets = sorted({t for (_, t, _) in D})
        pid = {}
        for (s, t, k), d in D.items():
            if t in pid:
                assert np.array_equal(pid[t], d["pid"])
            else:
                pid[t] = d["pid"]
        inv = {t: np.unique(pid[t], return_inverse=True) for t in targets}
        need = {"spru", best, "resid_phys", "resid_rand", "source"}
        preps = {(s, t, k, m): prep_auc(d["y"].astype(int), d[key(PRIMARY, m)]) for (s, t, k), d in D.items() for m in need
                 if ttype(s, t) in ("X", "W")}
        rng = np.random.default_rng(0); reps = []
        for _ in range(a.nboot):
            w = {}
            for t in targets:
                u, iv = inv[t]; w[t] = np.bincount(rng.integers(0, len(u), len(u)), minlength=len(u)).astype(float)[iv]
            aw = lambda s, t, k, kk: auc_w(preps[(s, t, k, kk)], w[t])
            sx, sw = {}, {}
            for m in need:
                f = lambda s, t, k, kk, m=m: aw(s, t, k, m)
                trsX = sorted({(s, t) for (s, t, k) in D if ttype(s, t) == "X"}); trsW = sorted({(s, t) for (s, t, k) in D if ttype(s, t) == "W"})
                sx[m] = np.mean([np.mean([f(s, t, k, m) for (s2, t2, k) in D if (s2, t2) == (s, t)]) for (s, t) in trsX])
                sw[m] = np.mean([np.mean([f(s, t, k, m) for (s2, t2, k) in D if (s2, t2) == (s, t)]) for (s, t) in trsW])
            reps.append({"H12": sx["spru"] - sx[best], "H13_phys": sx["spru"] - sx["resid_phys"],
                         "H13_rand": sx["spru"] - sx["resid_rand"],
                         "H14": (sx["spru"] - sx["source"]) - (sw["spru"] - sw["source"])})
        cw = R["curves"][f"W_{PRIMARY}"]
        pts = {"H12": cx["spru"] - cx[best], "H13_phys": cx["spru"] - cx["resid_phys"], "H13_rand": cx["spru"] - cx["resid_rand"],
               "H14": (cx["spru"] - cx["source"]) - (cw["spru"] - cw["source"])}
        for h, v in pts.items():
            arr = np.array([r[h] for r in reps]); lo, hi = np.quantile(arr, [0.025, 0.975])
            tests[f"{h}_{task}"] = dict(est=float(v), lo=float(lo), hi=float(hi),
                                        p=float(max(2 * min((arr <= 0).mean(), (arr >= 0).mean()), 1 / len(arr))))
    for fam in (["H12_T1", "H12_T2"], ["H13_phys_T1", "H13_rand_T1", "H13_phys_T2", "H13_rand_T2"]):
        ks = [k for k in fam if k in tests]
        for k, h in zip(ks, S.holm([tests[k]["p"] for k in ks])):
            tests[k]["p_holm"] = h
    res["tests"] = tests
    (ROOT / f"results/analysis/v7_{a.phase}.json").write_text(json.dumps(res, indent=1))
    L = [f"# plan_v7 {a.phase} (nboot {a.nboot})", ""]
    for task, R in res["tasks"].items():
        L += [f"## {task} ({R['n_jobs']} jobs; best baseline at n={PRIMARY}, X: {R['best_baseline']})", "",
              "| type_n | " + " | ".join(METHODS) + " |", "|---" * (len(METHODS) + 1) + "|"]
        for k, v in R["curves"].items():
            L.append(f"| {k} | " + " | ".join(f"{v[m]:.4f}" for m in METHODS) + " |")
        L.append("")
    L += ["| test | estimate | 95% CI | p | p (Holm) |", "|---|---|---|---|---|"]
    for k, v in tests.items():
        L.append(f"| {k} | {v['est']:.4f} | [{v['lo']:.4f}, {v['hi']:.4f}] | {v['p']:.4f} | {v.get('p_holm', float('nan')):.4f} |")
    (ROOT / f"tables/v7_{a.phase}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
