#!/usr/bin/env python3
"""Subgroup error analysis of the D9 diagnostic models (validation only).
Patient types: prevalent = SepsisLabel already 1 at the first recorded hour; incident = becomes 1 later;
non-septic. Also: left-truncated records (first ICULOS > 1)."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from src import stats as S
feat = pd.read_parquet(ROOT/"data/processed/features_v1.parquet", columns=["pid","hospital","y","ICULOS_raw","unit"])
sp = pd.read_csv(ROOT/"data/processed/splits_v1.csv", dtype={"pid":str})
feat = feat.merge(sp[["pid","split"]], on="pid", how="left")
first = feat.groupby("pid").agg(fy=("y","first"), sep=("y","max"), f_icu=("ICULOS_raw","min"))
first["ptype"] = np.where(first.sep==0, "nonseptic", np.where(first.fy==1, "prevalent", "incident"))
feat = feat.join(first[["ptype","f_icu"]], on="pid")
on = feat[feat.y==1].groupby("pid").ICULOS_raw.min()
feat["t_rel"] = feat.ICULOS_raw - feat.pid.map(on)  # hours relative to first positive label (NaN for nonseptic)
rows = []
for name in ["all","no_process","no_iculos","vitals_only","process_only"]:
    for src,tgt in (("A","B"),("B","A")):
        vid=f"diag_{name}_{src}2{tgt}_s0"
        for which,h,suffix in (("internal",src,"int"),("external",tgt,"ext")):
            d = feat[(feat.hospital==h)&(feat.split=="val")].copy()
            d["p"] = np.load(ROOT/f"results/diagnosis/{vid}_pred_{suffix}.npy")
            def au(m):
                x=d[m]; return S.auroc(x.y,x.p) if x.y.nunique()==2 else np.nan
            r=dict(variant=name, direction=f"{src}2{tgt}", eval=which, hosp=h,
                   all=au(d.index==d.index),
                   incident_vs_non=au(d.ptype!="prevalent"),
                   prevalent_vs_non=au(d.ptype!="incident"),
                   incident_pre6=au((d.ptype=="nonseptic")|((d.ptype=="incident")&(d.t_rel<0))),
                   notrunc=au(d.f_icu==1), trunc=au(d.f_icu>1),
                   frac_pos_rows_prevalent=float((d[(d.y==1)].ptype=="prevalent").mean()))
            rows.append(r)
out=pd.DataFrame(rows); pd.set_option("display.width",250)
print(out.round(3).to_string(index=False))
out.to_csv(ROOT/"results/diagnosis/subgroups_s0.csv", index=False)
