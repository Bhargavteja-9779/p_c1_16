#!/usr/bin/env python3
"""Prototype (validation only): per-site quantile normalization of features fitted on each site's
UNLABELED train rows; train on source, evaluate on target-val. Variants: which feature groups are normalized."""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd, lightgbm as lgb
from sklearn.metrics import roc_auc_score
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT)); sys.argv=[sys.argv[0]]
import importlib.util
spec = importlib.util.spec_from_file_location("db", ROOT/"scripts/diagnose_baseline.py"); db = importlib.util.module_from_spec(spec); spec.loader.exec_module(db)
t0=time.time(); feat, groups = db.features(); cols = db.variant_cols(groups, "all")
def qnorm(feat, cset):
    f = feat.copy()
    for h in "AB":
        m = f.hospital==h; ref = f.loc[m & (f.split=="train")]
        for c in cset:
            r = np.sort(ref[c].dropna().values)
            if len(r)==0: continue
            x = f.loc[m, c].values
            q = (np.searchsorted(r, x, "left") + np.searchsorted(r, x, "right"))/(2*len(r))
            f.loc[m, c] = np.where(np.isnan(x), np.nan, q).astype(np.float32)
    return f
res={}
for tag, cset in (("value+trend", groups["value"]+groups["trend"]), ("value+trend+context", groups["value"]+groups["trend"]+["Age","HospAdmTime","ICULOS"]),
                  ("everything", cols)):
    f = qnorm(feat, cset)
    for src,tgt in (("A","B"),("B","A")):
        tr=f[(f.hospital==src)&(f.split=="train")]; va=f[(f.hospital==src)&(f.split=="val")]; ex=f[(f.hospital==tgt)&(f.split=="val")]
        dtr=lgb.Dataset(tr[cols],tr.y); m=lgb.train({**db.PARAMS,"seed":0},dtr,2000,valid_sets=[lgb.Dataset(va[cols],va.y,reference=dtr)],callbacks=[lgb.early_stopping(100,verbose=False)])
        r=(roc_auc_score(va.y,m.predict(va[cols],num_iteration=m.best_iteration)), roc_auc_score(ex.y,m.predict(ex[cols],num_iteration=m.best_iteration)))
        res[f"{tag}_{src}2{tgt}"]=r; print(tag,src,tgt,np.round(r,3),flush=True)
json.dump(res, open(ROOT/"results/diagnosis/proto_sitenorm_s0.json","w"), indent=1); db.add_budget(time.time()-t0)
