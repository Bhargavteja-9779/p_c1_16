#!/usr/bin/env python3
"""Diagnosis step 2 (validation only). For the 'all' feature set:
 (1) pooled A+B training evaluated on each hospital's val (is the conditional shift learnable from both sites?)
 (2) covariate-shift-only prediction of external AUROC: patient-level domain classifier (source-train vs
     target-train features at each row) -> importance weights -> weighted AUROC on source-val.
     If this reproduces the observed external AUROC, case-mix explains the drop; if not, P(y|x) changed.
 (3) seed spread of external AUROC (seeds 0,1,2)."""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd, lightgbm as lgb
from sklearn.metrics import roc_auc_score
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
sys.argv = [sys.argv[0]]
import importlib.util
spec = importlib.util.spec_from_file_location("db", ROOT/"scripts/diagnose_baseline.py"); db = importlib.util.module_from_spec(spec); spec.loader.exec_module(db)
t0=time.time()
feat, groups = db.features(); cols = db.variant_cols(groups, "all")
P = db.PARAMS
out = {}
def fit(tr, va, seed):
    dtr = lgb.Dataset(tr[cols], tr["y"]); dva = lgb.Dataset(va[cols], va["y"], reference=dtr)
    return lgb.train({**P, "seed": seed}, dtr, 2000, valid_sets=[dva], callbacks=[lgb.early_stopping(100, verbose=False)])
V = {h: feat[(feat.hospital==h)&(feat.split=="val")] for h in "AB"}
T = {h: feat[(feat.hospital==h)&(feat.split=="train")] for h in "AB"}
# (1) pooled
m = fit(pd.concat([T["A"],T["B"]]), pd.concat([V["A"],V["B"]]), 0)
out["pooled"] = {h: roc_auc_score(V[h].y, m.predict(V[h][cols], num_iteration=m.best_iteration)) for h in "AB"}
print("pooled", out["pooled"], flush=True)
# (3) seeds
out["seeds"] = {}
for src,tgt in (("A","B"),("B","A")):
    r=[]
    for s in (0,1,2):
        m = fit(T[src], V[src], s)
        r.append((roc_auc_score(V[src].y, m.predict(V[src][cols], num_iteration=m.best_iteration)),
                  roc_auc_score(V[tgt].y, m.predict(V[tgt][cols], num_iteration=m.best_iteration))))
    out["seeds"][f"{src}2{tgt}"] = r; print(src, tgt, r, flush=True)
# (2) importance weighting with a domain classifier trained on train portions (no labels used)
out["iw"] = {}
dcols = [c for c in cols if c not in groups["process"]]  # also report with process features
for tag, cset in (("all_feats", cols), ("no_process_feats", dcols)):
    X = pd.concat([T["A"][cset], T["B"][cset]]); d = np.r_[np.zeros(len(T["A"])), np.ones(len(T["B"]))]
    dm = lgb.train({**P, "seed": 0, "learning_rate": 0.1}, lgb.Dataset(X, d), 200)
    for src,tgt in (("A","B"),("B","A")):
        pB = np.clip(dm.predict(V[src][cset]), 1e-4, 1-1e-4)
        w = pB/(1-pB) if tgt=="B" else (1-pB)/pB
        w = np.minimum(w, np.quantile(w, 0.99))
        pi = np.load(ROOT/f"results/diagnosis/diag_all_{src}2{tgt}_s0_pred_int.npy")
        obs = json.load(open(ROOT/f"results/diagnosis/diag_all_{src}2{tgt}_s0.json"))
        dauc = roc_auc_score(np.r_[np.zeros(len(V[src])), np.ones(len(V[tgt]))], np.r_[dm.predict(V[src][cset]), dm.predict(V[tgt][cset])])
        dauc = dauc if tgt=="B" else 1-dauc
        r = dict(domain_auc=dauc, internal=roc_auc_score(V[src].y, pi), iw_estimate=roc_auc_score(V[src].y, pi, sample_weight=w),
                 observed_external=obs["external"]["auroc"], ess_frac=float(w.sum()**2/(w**2).sum()/len(w)))
        out["iw"][f"{tag}_{src}2{tgt}"] = r; print(tag, src, tgt, r, flush=True)
json.dump(out, open(ROOT/"results/diagnosis/shift_s0.json","w"), indent=1)
db.add_budget(time.time()-t0)
