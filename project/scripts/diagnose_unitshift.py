#!/usr/bin/env python3
"""Control diagnosis (validation only): within-hospital ICU-unit transfer (MICU<->SICU), same encoding.
Train on hospital h, unit u (train split), early-stop on h/u val; evaluate on h/u val, h/other-unit val,
and other-hospital/same-unit val. Also: per-unit sepsis prevalence."""
import json, sys, time
from pathlib import Path
import numpy as np, pandas as pd, lightgbm as lgb
from sklearn.metrics import roc_auc_score
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT)); sys.argv=[sys.argv[0]]
import importlib.util
spec = importlib.util.spec_from_file_location("db", ROOT/"scripts/diagnose_baseline.py"); db = importlib.util.module_from_spec(spec); spec.loader.exec_module(db)
t0=time.time(); feat, groups = db.features(); cols=db.variant_cols(groups,"all")
# unit is constant per patient? take patient's first non-UNK unit
pu = feat[feat.unit!="UNK"].groupby("pid").unit.first()
feat["punit"] = feat.pid.map(pu).fillna("UNK")
print(feat.groupby(["hospital","punit"]).agg(pat=("pid","nunique"), prev=("y","mean")).round(4))
res={}
for h in "AB":
    for u,v in (("MICU","SICU"),("SICU","MICU")):
        o = "B" if h=="A" else "A"
        S=lambda hh,uu,sp: feat[(feat.hospital==hh)&(feat.punit==uu)&(feat.split==sp)]
        tr,va=S(h,u,"train"),S(h,u,"val")
        m=lgb.train({**db.PARAMS,"seed":0},lgb.Dataset(tr[cols],tr.y),2000,valid_sets=[lgb.Dataset(va[cols],va.y)],callbacks=[lgb.early_stopping(100,verbose=False)])
        ev={k:roc_auc_score(d.y,m.predict(d[cols],num_iteration=m.best_iteration)) for k,d in
            {"internal":va,"other_unit_same_hosp":S(h,v,"val"),"same_unit_other_hosp":S(o,u,"val"),"local_ref_other_unit":None}.items() if d is not None}
        res[f"{h}_{u}"]=ev; print(h,u,{k:round(x,3) for k,x in ev.items()},flush=True)
json.dump(res,open(ROOT/"results/diagnosis/unitshift_s0.json","w"),indent=1); db.add_budget(time.time()-t0)
