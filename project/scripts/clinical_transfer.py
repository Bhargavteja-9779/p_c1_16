#!/usr/bin/env python3
"""POST-HOC (review round 2): deployment-realistic clinical translation of E6 (test predictions, frozen models).

Threshold transfer: for each source model, the alert threshold is fixed at 90% patient-level specificity on the
SOURCE cell's own held-out test stays (the source model's local predictions; no target labels), then applied
unchanged in the target. Patient-level outcomes in the target:
  specificity_real  = share of non-septic stays that never alert
  timely_sensitivity = share of septic stays with a first alert at or before onset (onset = first positive
                       SepsisLabel hour + 6 h, the Challenge definition)
  lead_h            = median hours from first alert to onset among timely-detected stays
  alerts_per_100    = alerting stays per 100 stays
Also: calibration-slope contrast with CI (site vs population transfer), patient-cluster bootstrap (300 reps),
slope fitted by 1-D logistic regression of y on logit(p) per seed, averaged over seeds.
Writes results/analysis/clinical_transfer_E6.json, tables/clinical_transfer_E6.md.
"""
import glob, json
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
CELLS = ["A_MICU", "A_SICU", "B_MICU", "B_SICU"]; OH, OU = {"A": "B", "B": "A"}, {"MICU": "SICU", "SICU": "MICU"}
roles = lambda t: {"local": t, "unit": f"{t[0]}_{OU[t[2:]]}", "site": f"{OH[t[0]]}_{t[2:]}"}


def load(model):
    P = {}
    for f in glob.glob(str(ROOT / f"results/preds/E6_confirm__{model}__none__*__test.npz")):
        p = Path(f).stem.split("__"); P.setdefault(int(p[4][1:]), {})[p[3]] = dict(np.load(f, allow_pickle=True))
    return P


def stays(z, t):
    """per-stay arrays for target t from one prediction file: pid order, label, onset row idx, max score, row scores."""
    pid = z[f"{t}__pid"].astype(str); y = z[f"{t}__y"].astype(int); p = z[f"{t}__p"].astype(float)
    df = pd.DataFrame({"pid": pid, "y": y, "p": p}); df["i"] = df.groupby("pid").cumcount()
    return df


def thr_at_spec(df, spec=0.90):
    m = df.groupby("pid").agg(y=("y", "max"), p=("p", "max"))
    return float(np.quantile(m.p[m.y == 0], spec))


def outcomes(df, thr):
    g = df.groupby("pid")
    sep = g.y.max(); first_pos = df[df.y == 1].groupby("pid").i.min(); onset = first_pos + 6
    first_alert = df[df.p > thr].groupby("pid").i.min()
    neg = sep.index[sep == 0]; pos = sep.index[sep == 1]
    spec = float(1 - first_alert.reindex(neg).notna().mean())
    fa = first_alert.reindex(pos); timely = (fa <= onset.reindex(pos)) & fa.notna()
    lead = (onset.reindex(pos) - fa)[timely]
    return dict(specificity_real=spec, timely_sensitivity=float(timely.mean()), lead_h=float(lead.median()) if len(lead) else None,
                alerts_per_100=float(100 * first_alert.reindex(sep.index).notna().mean()))


def slope(y, p):
    x = np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6))); a, b = 0.0, 1.0
    for _ in range(25):
        eta = a + b * x; mu = 1 / (1 + np.exp(-eta)); w = mu * (1 - mu) + 1e-9
        g = np.array([np.sum(y - mu), np.sum((y - mu) * x)]); H = np.array([[w.sum(), (w * x).sum()], [(w * x).sum(), (w * x * x).sum()]])
        d = np.linalg.solve(H, g); a, b = a + d[0], b + d[1]
        if np.abs(d).max() < 1e-7: break
    return b


R = {"definition": __doc__.split("\n\n")[1].strip(), "models": {}}
rng = np.random.default_rng(3)
for model in ("lgbm", "lr"):
    P = load(model); seeds = sorted(P); res = {r: [] for r in ("local", "unit", "site")}
    for s in seeds:
        for t in CELLS:
            for r, c in roles(t).items():
                thr = thr_at_spec(stays(P[s][c], c))           # threshold on source cell's own test stays
                res[r].append(outcomes(stays(P[s][c], t), thr))
    agg = {r: {k: float(np.nanmean([o[k] for o in v if o[k] is not None])) for k in v[0]} for r, v in res.items()}
    # calibration slope contrast with patient-cluster bootstrap
    data = {}
    for t in CELLS:
        z0 = P[seeds[0]][t]; pid = z0[f"{t}__pid"].astype(str); y = z0[f"{t}__y"].astype(int)
        up, inv = np.unique(pid, return_inverse=True)
        data[t] = (y, inv, len(up), {r: [P[s][c][f"{t}__p"].astype(float) for s in seeds] for r, c in roles(t).items()})
    def cs(idx_by_t):
        out = {}
        for r in ("unit", "site"):
            out[r] = np.mean([np.mean([slope(data[t][0][idx_by_t[t]], v[idx_by_t[t]]) for v in data[t][3][r]]) for t in CELLS])
        return out["unit"] - out["site"], out
    pt, parts = cs({t: np.arange(len(data[t][0])) for t in CELLS}); bs = []
    for _ in range(300):
        idx = {}
        for t in CELLS:
            y, inv, n, _ = data[t]; pick = rng.integers(0, n, n)
            rows = np.concatenate([np.flatnonzero(inv == k) for k in pick]) if n < 0 else None
            # fast cluster resample: weights via repeated row indices
            cnt = np.bincount(pick, minlength=n); idx[t] = np.repeat(np.arange(len(inv)), cnt[inv])
        bs.append(cs(idx)[0])
    agg["calslope_unit_minus_site"] = dict(estimate=float(pt), ci95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))],
                                          slope_unit=float(parts["unit"]), slope_site=float(parts["site"]))
    R["models"][model] = agg
(ROOT / "results/analysis/clinical_transfer_E6.json").write_text(json.dumps(R, indent=1))
L = ["# POST HOC: source-transferred thresholds (90% specificity on source held-out stays), E6 test predictions\n",
     "| model | source | real specificity in target | timely sensitivity (alert ≤ onset) | median lead time, h | alerting stays per 100 |", "|---|---|---|---|---|---|"]
for m, a in R["models"].items():
    for r, lab in (("local", "local"), ("unit", "other unit, same hospital"), ("site", "same unit, other hospital")):
        o = a[r]; L.append(f"| {m} | {lab} | {o['specificity_real']:.3f} | {o['timely_sensitivity']:.3f} | {o['lead_h']:.1f} | {o['alerts_per_100']:.1f} |")
L += ["", "| model | calibration slope, population transfer | calibration slope, site transfer | difference (95% CI) |", "|---|---|---|---|"]
for m, a in R["models"].items():
    c = a["calslope_unit_minus_site"]; L.append(f"| {m} | {c['slope_unit']:.3f} | {c['slope_site']:.3f} | {c['estimate']:.3f} [{c['ci95'][0]:.3f}, {c['ci95'][1]:.3f}] |")
(ROOT / "tables/clinical_transfer_E6.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
