#!/usr/bin/env python3
"""POST-HOC clinical translation of the E6 site excess (added after review round 1; not pre-registered).

Patient-level alerting (a stay alerts if its maximum hourly risk exceeds the threshold). For each target cell the
threshold is set so that 10% of non-septic target patients alert (specificity 0.90, set on the target itself for
every model, i.e. an optimistic, recalibrated deployment). Metric: sensitivity (share of septic stays alerted).
D_sens = sensitivity(population-transfer model) - sensitivity(site-transfer model); also gaps vs the local model.
Averaged over seeds 100-104 and the 4 target cells; patient-cluster bootstrap (1000) within target cells.
Writes results/analysis/clinical_E6.json and tables/clinical_E6.md.
"""
import glob, json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
CELLS = ["A_MICU", "A_SICU", "B_MICU", "B_SICU"]
OH, OU = {"A": "B", "B": "A"}, {"MICU": "SICU", "SICU": "MICU"}
roles = lambda t: {"local": t, "unit": f"{t[0]}_{OU[t[2:]]}", "site": f"{OH[t[0]]}_{t[2:]}"}


def load(model):
    P = {}
    for f in glob.glob(str(ROOT / f"results/preds/E6_confirm__{model}__none__*__test.npz")):
        p = Path(f).stem.split("__"); P.setdefault(int(p[4][1:]), {})[p[3]] = dict(np.load(f, allow_pickle=True))
    return P


def patient(P, t):
    """per target: patient ids, labels, and per role a (seeds x patients) matrix of max risk."""
    s0 = sorted(P)[0]; pid = P[s0][t][f"{t}__pid"].astype(str); y = P[s0][t][f"{t}__y"]
    df = pd.DataFrame({"pid": pid, "y": y}); g = df.groupby("pid", sort=True).y.max()
    out = {}
    for r, c in roles(t).items():
        M = []
        for s in sorted(P):
            z = P[s][c]; assert (z[f"{t}__pid"].astype(str) == pid).all()
            M.append(pd.Series(z[f"{t}__p"]).groupby(pid).max().reindex(g.index).values)
        out[r] = np.vstack(M)
    return g.values.astype(int), out


def sens_at_spec(y, p, w, spec=0.90):
    neg = p[y == 0]; wn = w[y == 0]; o = np.argsort(neg); cw = np.cumsum(wn[o]) / wn.sum()
    thr = neg[o][min(np.searchsorted(cw, spec), len(o) - 1)]
    return float((w[(y == 1)] * (p[y == 1] > thr)).sum() / w[y == 1].sum())


def run(model, nboot, rng):
    P = load(model); data = {t: patient(P, t) for t in CELLS}
    def stat(ws):
        res = {}
        for t in CELLS:
            y, S = data[t]; w = ws[t]
            res[t] = {r: np.mean([sens_at_spec(y, row, w) for row in S[r]]) for r in S}
        m = {r: np.mean([res[t][r] for t in CELLS]) for r in ("local", "unit", "site")}
        return dict(sens_local=m["local"], sens_unit=m["unit"], sens_site=m["site"], gap_unit=m["local"] - m["unit"],
                    gap_site=m["local"] - m["site"], D_sens=m["unit"] - m["site"])
    pt = stat({t: np.ones(len(data[t][0])) for t in CELLS})
    bs = []
    for _ in range(nboot):
        ws = {t: np.bincount(rng.integers(0, len(data[t][0]), len(data[t][0])), minlength=len(data[t][0])).astype(float) for t in CELLS}
        bs.append(stat(ws))
    out = {}
    for k in pt:
        v = np.array([b[k] for b in bs]); out[k] = dict(estimate=float(pt[k]), ci95=[float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))])
    return out


if __name__ == "__main__":
    rng = np.random.default_rng(1)
    R = {"definition": "patient-level sensitivity at 90% specificity (threshold set on each target); POST HOC", "seeds": [100, 101, 102, 103, 104]}
    for m in ("lgbm", "lr"):
        R[m] = run(m, 1000, rng)
    (ROOT / "results/analysis/clinical_E6.json").write_text(json.dumps(R, indent=1))
    L = ["# POST-HOC: sensitivity at 90% patient-level specificity (E6 test predictions)\n", "| model | local | population-transfer | site-transfer | gap population | gap site | D (sensitivity) |", "|---|---|---|---|---|---|---|"]
    for m in ("lgbm", "lr"):
        r = R[m]; f = lambda k: f"{r[k]['estimate']:.3f} [{r[k]['ci95'][0]:.3f}, {r[k]['ci95'][1]:.3f}]"
        L.append(f"| {m} | {r['sens_local']['estimate']:.3f} | {r['sens_unit']['estimate']:.3f} | {r['sens_site']['estimate']:.3f} | {f('gap_unit')} | {f('gap_site')} | {f('D_sens')} |")
    (ROOT / "tables/clinical_E6.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
