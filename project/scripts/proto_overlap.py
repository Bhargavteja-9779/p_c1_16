#!/usr/bin/env python3
"""Prototype (train portions only, no labels): how separable are A and B after removing encoding
fingerprints? Domain classifier on harmonised features (Calcium<2 -> NaN, Age floored, EtCO2 dropped)
with feature subsets. Reports domain AUC on val portions."""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd, lightgbm as lgb
from sklearn.metrics import roc_auc_score
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT)); sys.argv=[sys.argv[0]]
import importlib.util
spec = importlib.util.spec_from_file_location("db", ROOT/"scripts/diagnose_baseline.py"); db = importlib.util.module_from_spec(spec); spec.loader.exec_module(db)
t0=time.time()
feat = pd.read_parquet(ROOT/"data/processed/features_harm_v1.parquet"); groups=json.loads((ROOT/"data/processed/features_v1.groups.json").read_text())
sp = pd.read_csv(ROOT/"data/processed/splits_v1.csv", dtype={"pid":str}); feat=feat.merge(sp[["pid","split"]],on="pid")
from src.data_physionet2019 import VITALS
allc=[c for c in db.variant_cols(groups,"all") if not c.startswith("EtCO2")]
sets={"all_harm":allc,
 "no_process":[c for c in allc if c not in groups["process"]],
 "vitals_values_trends":[c for c in allc if c in groups["trend"] or (c in groups["value"] and c.split("_")[0] in VITALS)],
 "vitals+age_gender":[c for c in allc if c in groups["trend"] or (c in groups["value"] and c.split("_")[0] in VITALS)]+["Age","Gender"]}
res={}
for k,cols in sets.items():
    tr=feat[feat.split=="train"]; va=feat[feat.split=="val"]
    m=lgb.train({**db.PARAMS,"seed":0,"learning_rate":0.1},lgb.Dataset(tr[cols],(tr.hospital=="B").astype(int)),200)
    p=m.predict(va[cols]); auc=roc_auc_score(va.hospital=="B",p)
    imp=pd.Series(m.feature_importance("gain"),index=cols).sort_values(ascending=False)
    res[k]=dict(domain_auc=auc, frac_mid=float(((p>0.1)&(p<0.9)).mean()), top=(imp.head(8)/imp.sum()).round(3).to_dict())
    print(k, round(auc,4), res[k]["frac_mid"], list(res[k]["top"].items())[:5], flush=True)
json.dump(res,open(ROOT/"results/diagnosis/proto_overlap.json","w"),indent=1); db.add_budget(time.time()-t0)
