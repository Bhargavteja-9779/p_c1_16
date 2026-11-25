#!/usr/bin/env python3
"""G4: reproduce the published PhysioNet 2019 cross-hospital protocol (doi:10.20944/preprints202610.1449.v1,
abstract via OpenAlex; full text blocked, HTTP 403) as closely as its abstract allows. VALIDATION ONLY.

Published protocol (abstract): adult stays with >= 24 hourly records and no positive SepsisLabel in the first 12 h;
115 predictors from the first 12-h window; elastic-net LR, RF, XGBoost trained separately in A and B; evaluated
internally and in the other system without refitting. Reported XGBoost AUROC: A 0.725 -> A->B 0.608; B 0.702 -> B->A 0.636.
Cohort 30,646 stays, 1,843 subsequent sepsis events.

Our approximation (details not in the abstract are our choices, logged here): per variable over hours 1-12:
last non-missing (pandas groupby.last skips NaN), mean, min, max, n observed, missing indicator (vitals+labs), plus Age, Gender, HospAdmTime -> 40*6+3 = 243
columns. Label = any SepsisLabel = 1 after hour 12. Our pinned patient split: fit on source train, early stopping /
C selection on half of source val (fixed), internal AUROC on the other half of source val, external on the target's
same val half. Models: LightGBM (grid as frozen), L1/L2 elastic-net-ish LR (saga, l1_ratio 0.5, C grid).
Writes results/g4_reproduce.json.
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_physionet2019 import load, VITALS, LABS
from sklearn.metrics import roc_auc_score

raw = load().sort_values(["pid", "ICULOS"])
sp = pd.read_csv(ROOT / "data/processed/splits_v1.csv", dtype={"pid": str}).set_index("pid").split
g = raw.groupby("pid")
n = g.size(); early = raw[raw.ICULOS <= 12].groupby("pid").SepsisLabel.max()
coh = n[(n >= 24)].index.intersection(early[early == 0].index)
r = raw[raw.pid.isin(coh)]
w = r[r.ICULOS <= 12]; later = r[r.ICULOS > 12].groupby("pid").SepsisLabel.max()
V = VITALS + LABS
agg = w.groupby("pid")[V].agg(["last", "mean", "min", "max", "count"])
agg.columns = [f"{a}_{b}" for a, b in agg.columns]
for v in V:
    agg[f"{v}_miss"] = (agg[f"{v}_count"] == 0).astype(np.int8)
ctx = w.groupby("pid")[["Age", "Gender", "HospAdmTime"]].first()
X = agg.join(ctx); X["y"] = later.reindex(X.index).astype(int); X["h"] = r.groupby("pid").hospital.first()
X["split"] = sp.reindex(X.index)
cols = [c for c in X.columns if c not in ("y", "h", "split")]
rng = np.random.default_rng(0)
X["half"] = rng.integers(0, 2, len(X))  # fixed val halves: 0 = selection, 1 = evaluation
out = {"cohort_stays": int(len(X)), "events": int(X.y.sum()), "n_features": len(cols),
       "published": {"cohort": 30646, "events": 1843, "xgb_A_int": 0.725, "xgb_AtoB": 0.608, "xgb_B_int": 0.702, "xgb_BtoA": 0.636},
       "results": {}}


def fit_lgbm(tr, se):
    import lightgbm as lgb
    best = None
    for nl in (15, 63, 255):
        m = lgb.train(dict(objective="binary", learning_rate=0.05, num_leaves=nl, min_child_samples=50, feature_fraction=0.8,
                           bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0, verbose=-1, num_threads=4, seed=0),
                      lgb.Dataset(tr[cols], tr.y), 3000, valid_sets=[lgb.Dataset(se[cols], se.y)],
                      callbacks=[lgb.early_stopping(100, verbose=False)])
        a = roc_auc_score(se.y, m.predict(se[cols], num_iteration=m.best_iteration))
        if best is None or a > best[0]:
            best = (a, m)
    m = best[1]; return lambda d: m.predict(d[cols], num_iteration=m.best_iteration)


def fit_lr(tr, se):
    from sklearn.linear_model import LogisticRegression
    med = tr[cols].median(); mu = tr[cols].fillna(med).mean(); sd = tr[cols].fillna(med).std() + 1e-6
    T = lambda d: ((d[cols].fillna(med) - mu) / sd).fillna(0).clip(-10, 10).values
    best = None
    for C in (0.01, 0.1, 1.0):
        m = LogisticRegression(penalty="elasticnet", l1_ratio=0.5, C=C, solver="saga", max_iter=2000).fit(T(tr), tr.y)
        a = roc_auc_score(se.y, m.predict_proba(T(se))[:, 1])
        if best is None or a > best[0]:
            best = (a, m)
    m = best[1]; return lambda d: m.predict_proba(T(d))[:, 1]


for model, fit in (("lgbm", fit_lgbm), ("enet_lr", fit_lr)):
    for s, t in (("A", "B"), ("B", "A")):
        tr = X[(X.h == s) & (X.split == "train")]; se = X[(X.h == s) & (X.split == "val") & (X.half == 0)]
        pr = fit(tr, se)
        ev_i = X[(X.h == s) & (X.split == "val") & (X.half == 1)]; ev_e = X[(X.h == t) & (X.split == "val") & (X.half == 1)]
        out["results"][f"{model}_{s}"] = {"internal": float(roc_auc_score(ev_i.y, pr(ev_i))),
                                          f"{s}to{t}": float(roc_auc_score(ev_e.y, pr(ev_e))),
                                          "n_int": int(len(ev_i)), "n_ext": int(len(ev_e))}
        print(model, s, out["results"][f"{model}_{s}"], flush=True)
(ROOT / "results/g4_reproduce.json").write_text(json.dumps(out, indent=1))
print(json.dumps({k: out[k] for k in ("cohort_stays", "events", "n_features")}))
