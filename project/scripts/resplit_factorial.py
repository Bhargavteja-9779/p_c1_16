#!/usr/bin/env python3
"""plan_v9 / E15: site excess D over 10 alternative patient splits (see experiments/plan_v9.yaml). Idempotent:
per-(split, model, train cell) results cached in results/v9/. Then summary -> results/analysis/v9_resplit.json."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from src.train_eval import load_cells, fit_lgbm, fit_lr, CELLS
from scipy import stats
OUT = ROOT / "results/v9"; OUT.mkdir(parents=True, exist_ok=True)
OH, OU = {"A": "B", "B": "A"}, {"MICU": "SICU", "SICU": "MICU"}
feat, cols = load_cells("none")
pat = feat.groupby("pid").agg(h=("hospital", "first"), sep=("y", "max")).reset_index()


def split_for(seed):
    rng = np.random.default_rng(seed); sp = pd.Series("", index=pat.pid)
    for (h, s), d in pat.groupby(["h", "sep"]):
        ids = np.array(sorted(d.pid)); rng.shuffle(ids); n = len(ids); a, b = int(.6 * n), int(.8 * n)
        sp[ids[:a]] = "train"; sp[ids[a:b]] = "val"; sp[ids[b:]] = "test"
    return sp


for seed in range(3001, 3011):
    sp = split_for(seed); f = feat.assign(split=feat.pid.map(sp))
    for model, fit in (("lgbm", fit_lgbm), ("lr", fit_lr)):
        for c in CELLS:
            rf = OUT / f"E15__{model}__{c}__split{seed}.json"
            if rf.exists():
                continue
            tr = f[(f.cell == c) & (f.split == "train")]; va = f[(f.cell == c) & (f.split == "val")]
            pr, sel = fit(tr, va, cols, 0)
            from sklearn.metrics import roc_auc_score
            ev = {t: float(roc_auc_score(f[(f.cell == t) & (f.split == "test")].y, pr(f[(f.cell == t) & (f.split == "test")]))) for t in CELLS}
            rf.write_text(json.dumps(dict(model=model, train_cell=c, split_seed=seed, selection=sel, auroc=ev), indent=1)); print(rf.name, ev, flush=True)
R = {}
for model in ("lgbm", "lr"):
    Ds = []
    for seed in range(3001, 3011):
        A = {json.loads(p.read_text())["train_cell"]: json.loads(p.read_text())["auroc"] for p in OUT.glob(f"E15__{model}__*__split{seed}.json")}
        Ds.append(np.mean([A[f"{t[0]}_{OU[t[2:]]}"][t] - A[f"{OH[t[0]]}_{t[2:]}"][t] for t in CELLS]))
    Ds = np.array(Ds); m, sd = Ds.mean(), Ds.std(ddof=1); h = stats.t.ppf(.975, len(Ds) - 1) * sd / np.sqrt(len(Ds))
    p = 2 * stats.t.sf(abs(m / (sd / np.sqrt(len(Ds)))), len(Ds) - 1)
    R[model] = dict(D_per_split=Ds.round(4).tolist(), mean=float(m), sd_between_splits=float(sd), ci95=[float(m - h), float(m + h)], p=float(p), n_positive=int((Ds > 0).sum()))
ps = sorted(R, key=lambda k: R[k]["p"]); run = 0
for i, k in enumerate(ps):
    run = max(run, min(1, (len(ps) - i) * R[k]["p"])); R[k]["p_holm"] = run
(ROOT / "results/analysis/v9_resplit.json").write_text(json.dumps(R, indent=1))
L = ["# plan_v9 / E15: site excess over 10 alternative splits (test sets of each split, hour-level AUROC, model seed 0)\n", "| model | mean D | 95% CI (t, across splits) | between-split SD | splits with D > 0 | p | p (Holm) |", "|---|---|---|---|---|---|---|"]
for k, v in R.items():
    L.append(f"| {k} | {v['mean']:.3f} | [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}] | {v['sd_between_splits']:.3f} | {v['n_positive']}/10 | {v['p']:.4f} | {v['p_holm']:.4f} |")
(ROOT / "tables/v9_resplit.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
