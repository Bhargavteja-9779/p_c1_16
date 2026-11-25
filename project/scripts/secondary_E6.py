#!/usr/bin/env python3
"""E6 secondary outcomes (pre-registered in plan_v2 but not in the first draft) + POST-HOC pre-onset AUROC.
(1) From results/raw_results.csv (E6, test): AUROC, AUPRC, calibration slope and calibration-in-the-large by role
    (local / population-transfer / site-transfer / both), mean over 4 target cells and 5 seeds (seed SD reported).
(2) POST HOC (review round 1): early-warning AUROC excluding post-onset hours. In PhysioNet 2019 SepsisLabel = 1 from
    6 h before onset onward; for each septic stay we keep only its first 6 positive hours (the pre-onset window) and
    drop later positive hours. D_pre = AUROC(population source) - AUROC(site source) on these rows, patient-cluster
    bootstrap (1000). Writes results/analysis/secondary_E6.json and tables/secondary_E6.md."""
import glob, json
from pathlib import Path
import numpy as np, pandas as pd
import sys; ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT / "scripts"))
from analyze_transport import prep_auc, auc_w
CELLS = ["A_MICU", "A_SICU", "B_MICU", "B_SICU"]; OH, OU = {"A": "B", "B": "A"}, {"MICU": "SICU", "SICU": "MICU"}
role = lambda t: {"local": t, "unit": f"{t[0]}_{OU[t[2:]]}", "site": f"{OH[t[0]]}_{t[2:]}", "both": f"{OH[t[0]]}_{OU[t[2:]]}"}
raw = pd.read_csv(ROOT / "results/raw_results.csv"); e6 = raw[(raw.experiment == "E6_confirm") & (raw.fixes == "none")]
R = {"secondary": {}, "preonset": {}}
for m in ("lgbm", "lr"):
    d = e6[e6.model == m]; R["secondary"][m] = {}
    for r in ("local", "unit", "site", "both"):
        rows = pd.concat([d[(d.eval_cell == t) & (d.train_cell == role(t)[r])] for t in CELLS])
        bys = rows.groupby("seed")[["auroc", "auprc", "cal_slope", "citl"]].mean()
        R["secondary"][m][r] = {k: dict(mean=float(rows[k].mean()), seed_sd=float(bys[k].std(ddof=1))) for k in ("auroc", "auprc", "cal_slope", "citl")}
rng = np.random.default_rng(2)
for m in ("lgbm", "lr"):
    P = {}
    for f in glob.glob(str(ROOT / f"results/preds/E6_confirm__{m}__none__*__test.npz")):
        p = Path(f).stem.split("__"); P.setdefault(int(p[4][1:]), {})[p[3]] = dict(np.load(f, allow_pickle=True))
    data = {}
    for t in CELLS:
        z = P[100][t]; pid = z[f"{t}__pid"].astype(str); y = z[f"{t}__y"].astype(int)
        k = pd.Series(y).groupby(pid).cumsum().values  # running count of positive hours within stay (rows ordered by hour)
        keep = (y == 0) | (k <= 6)
        upid, inv = np.unique(pid[keep], return_inverse=True)
        S = {r: [P[s][c][f"{t}__p"][keep] for s in sorted(P)] for r, c in role(t).items()}
        data[t] = (y[keep], inv, len(upid), {r: [prep_auc(y[keep], v) for v in S[r]] for r in S})
    def stat(ws):
        a = {r: np.mean([np.mean([auc_w(pp, ws[t]) for pp in data[t][3][r]]) for t in CELLS]) for r in ("local", "unit", "site")}
        return dict(local=a["local"], unit=a["unit"], site=a["site"], gap_unit=a["local"] - a["unit"], gap_site=a["local"] - a["site"], D=a["unit"] - a["site"])
    pt = stat({t: np.ones(len(data[t][0])) for t in CELLS}); bs = []
    for _ in range(1000):
        ws = {t: np.bincount(rng.integers(0, data[t][2], data[t][2]), minlength=data[t][2])[data[t][1]].astype(float) for t in CELLS}
        bs.append(stat(ws))
    R["preonset"][m] = {k: dict(estimate=float(pt[k]), ci95=[float(np.percentile([b[k] for b in bs], 2.5)), float(np.percentile([b[k] for b in bs], 97.5))]) for k in pt}
(ROOT / "results/analysis/secondary_E6.json").write_text(json.dumps(R, indent=1))
L = ["# E6 secondary outcomes (test; mean of 4 target cells x 5 seeds; seed SD in parentheses)\n", "| model | role | AUROC | AUPRC | calibration slope | calibration-in-the-large |", "|---|---|---|---|---|---|"]
for m in R["secondary"]:
    for r, v in R["secondary"][m].items():
        L.append(f"| {m} | {r} | " + " | ".join(f"{v[k]['mean']:.3f} ({v[k]['seed_sd']:.3f})" for k in ("auroc", "auprc", "cal_slope", "citl")) + " |")
L += ["", "# POST HOC: pre-onset hour-level AUROC (post-onset positive hours removed)\n", "| model | local | population source | site source | gap population | gap site | D |", "|---|---|---|---|---|---|---|"]
for m, v in R["preonset"].items():
    f = lambda k: f"{v[k]['estimate']:.3f} [{v[k]['ci95'][0]:.3f}, {v[k]['ci95'][1]:.3f}]"
    L.append(f"| {m} | {v['local']['estimate']:.3f} | {v['unit']['estimate']:.3f} | {v['site']['estimate']:.3f} | {f('gap_unit')} | {f('gap_site')} | {f('D')} |")
(ROOT / "tables/secondary_E6.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
