#!/usr/bin/env python3
"""Prototype (validation only): does repairing obvious encoding artefacts change A<->B transport?
repair: Calcium<2 -> NaN (ionised mmol/L mixed into total mg/dL, B only); drop TroponinI, Bilirubin_direct, EtCO2
features; Age floored in both sites."""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd, lightgbm as lgb
from sklearn.metrics import roc_auc_score
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT)); sys.argv=[sys.argv[0]]
import importlib.util
spec = importlib.util.spec_from_file_location("db", ROOT/"scripts/diagnose_baseline.py"); db = importlib.util.module_from_spec(spec); spec.loader.exec_module(db)
from src.data_physionet2019 import load
from src.features import build_features
t0=time.time()
cache = ROOT/"data/processed/features_harm_v1.parquet"
if cache.exists():
    feat = pd.read_parquet(cache); groups = json.loads((ROOT/"data/processed/features_v1.groups.json").read_text())
else:
    raw = load(); raw.loc[raw.Calcium < 2, "Calcium"] = np.nan; raw["Age"] = np.floor(raw["Age"])
    feat, groups = build_features(raw); feat.to_parquet(cache)
sp = pd.read_csv(ROOT/"data/processed/splits_v1.csv", dtype={"pid":str}); feat = feat.merge(sp[["pid","split"]], on="pid")
drop = [c for c in db.variant_cols(groups,"all") if c.split("_")[0] in ("TroponinI","EtCO2") or c.startswith("Bilirubin_direct")]
res={}
for tag in ("calcium+age_repaired", "repaired+drop3"):
    cols = db.variant_cols(groups,"all"); cols = [c for c in cols if c not in drop] if tag.endswith("drop3") else cols
    for src,tgt in (("A","B"),("B","A")):
        tr=feat[(feat.hospital==src)&(feat.split=="train")]; va=feat[(feat.hospital==src)&(feat.split=="val")]; ex=feat[(feat.hospital==tgt)&(feat.split=="val")]
        dtr=lgb.Dataset(tr[cols],tr.y); m=lgb.train({**db.PARAMS,"seed":0},dtr,2000,valid_sets=[lgb.Dataset(va[cols],va.y,reference=dtr)],callbacks=[lgb.early_stopping(100,verbose=False)])
        r=(roc_auc_score(va.y,m.predict(va[cols],num_iteration=m.best_iteration)), roc_auc_score(ex.y,m.predict(ex[cols],num_iteration=m.best_iteration)))
        res[f"{tag}_{src}2{tgt}"]=r; print(tag,src,tgt,np.round(r,3),flush=True)
json.dump(res, open(ROOT/"results/diagnosis/proto_harmonise_s0.json","w"), indent=1); db.add_budget(time.time()-t0)
