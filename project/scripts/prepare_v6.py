#!/usr/bin/env python3
"""plan_v6 data: task T2 = hypotension early warning (MAP < 65 mmHg within the next 6 h) on three open ICU databases
(PhysioNet 2019 hospital systems A = BIDMC and B = Emory; PhysioNet 2012 = MIMIC-II, here 'M'), units MICU/SICU.

Definitions (fixed in experiments/plan_v6.yaml before any model was fitted):
  * stays: ICU data covering hour 48 (2019: max ICULOS >= 48; 2012: all stays, which are >= 48 h by construction);
    only hours 1..48 are used (2012 provides only the first 48 h).
  * prediction hours t = 6..42. Eligible if MAP was observed in (t-2, t] with last value >= 65 (not currently
    hypotensive) and at least one MAP is observed in (t, t+6] (label defined by a measurement, not by its absence).
  * label y = 1 if any hourly MAP in (t, t+6] < 65.
  * features: src.features.build_features on the 24 variables common to both databases (no SpO2, EtCO2, ...);
    context = Age, Gender, ICULOS (HospAdmTime does not exist in 2012).
  * split: 2019 patients keep the pinned v1 split (configs/splits_v1.csv) so v1 test patients stay test;
    2012 patients get 60/20/20 by (unit, ever-positive), SPLIT_SEED 2027, pinned to configs/splits_v6_m.csv.
Output: data/processed/features_v6.parquet (+ .groups.json). Idempotent.
"""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import data_physionet2019 as d19, data_physionet2012 as d12, features as F

COMMON = ["HR", "Temp", "SBP", "MAP", "DBP", "Resp", "FiO2", "pH", "PaCO2", "SaO2", "AST", "BUN", "Alkalinephos",
          "Creatinine", "Glucose", "Lactate", "Magnesium", "Potassium", "Bilirubin_total", "TroponinI", "Hct",
          "Platelets", "WBC", "HCO3"]
OUT = ROOT / "data/processed/features_v6.parquet"


def main():
    if OUT.exists():
        print("exists", OUT); return
    a = d19.load()
    los = a.groupby("pid").ICULOS.transform("max")
    a = a[(los >= 48) & (a.ICULOS <= 48)].copy()
    a["unit"] = np.where(a.Unit1 == 1, "MICU", np.where(a.Unit2 == 1, "SICU", "UNK"))
    a["site"] = a.hospital
    m = d12.load()
    m["site"] = "M"
    keep = ["pid", "site", "unit", "ICULOS", "Age", "Gender"] + COMMON
    df = pd.concat([a[keep], m[keep]], ignore_index=True)
    pu = df.groupby("pid").unit.agg(lambda s: s[s != "UNK"].iloc[0] if (s != "UNK").any() else "UNK")
    df["unit"] = df.pid.map(pu)
    df = df[df.unit.isin(["MICU", "SICU"])].sort_values(["pid", "ICULOS"]).reset_index(drop=True)
    # label: future MAP minimum in (t, t+6]
    g = df.groupby("pid", sort=False).MAP
    fut = pd.concat([g.shift(-k) for k in range(1, 7)], axis=1)
    df["fut_min"] = fut.min(axis=1)
    df["fut_n"] = fut.notna().sum(axis=1)
    recent = pd.concat([g.shift(k) for k in range(0, 2)], axis=1)  # hours t and t-1
    last_recent = recent.bfill(axis=1).iloc[:, 0]
    # adapt to build_features (expects 2019 column set): add absent vars as NaN, then restrict features later
    tmp = df.rename(columns={"site": "hospital"}).copy()
    for v in d19.VITALS + d19.LABS:
        if v not in tmp:
            tmp[v] = np.nan
    tmp["HospAdmTime"] = np.nan
    tmp["Unit1"] = (tmp.unit == "MICU").astype(float); tmp["Unit2"] = (tmp.unit == "SICU").astype(float)
    tmp["SepsisLabel"] = 0
    feat, groups = F.build_features(tmp)
    assert (feat.pid.values == df.pid.values).all() and (feat.ICULOS_raw.values == df.ICULOS.values).all()
    feat["site"] = df.site.values; feat["unit"] = df.unit.values; feat["cell"] = df.site.values + "_" + df.unit.values
    feat["y"] = (df.fut_min.values < 65).astype(np.int8)
    elig = (df.ICULOS.between(6, 42)) & (last_recent >= 65) & (df.fut_n > 0)
    feat = feat[elig.values].reset_index(drop=True)
    keepf = lambda c: c.split("_")[0] in COMMON or c.rsplit("_", 1)[0] in COMMON
    groups = {k: [c for c in v if keepf(c)] for k, v in groups.items() if k != "context"}
    groups["context"] = ["Age", "Gender", "ICULOS"]
    # splits
    sp1 = pd.read_csv(ROOT / "configs/splits_v1.csv", dtype={"pid": str})[["pid", "split"]]
    pm = ROOT / "configs/splits_v6_m.csv"
    if not pm.exists():
        pat = feat[feat.site == "M"].groupby("pid").agg(unit=("unit", "first"), pos=("y", "max")).reset_index()
        rng = np.random.default_rng(2027); pat["split"] = ""
        for _, idx in pat.groupby(["unit", "pos"]).groups.items():
            idx = np.array(sorted(idx)); rng.shuffle(idx); n = len(idx)
            pat.loc[idx[:int(.6 * n)], "split"] = "train"; pat.loc[idx[int(.6 * n):int(.8 * n)], "split"] = "val"
            pat.loc[idx[int(.8 * n):], "split"] = "test"
        pat[["pid", "split"]].to_csv(pm, index=False)
    sp = pd.concat([sp1, pd.read_csv(pm, dtype={"pid": str})], ignore_index=True)
    feat = feat.merge(sp, on="pid", how="left")
    assert feat.split.notna().all(), "patients without split"
    feat.to_parquet(OUT)
    (OUT.with_suffix(".groups.json")).write_text(json.dumps(groups, indent=1))
    s = feat.groupby(["cell", "split"]).agg(rows=("y", "size"), pos=("y", "sum"), pats=("pid", "nunique"))
    print(s.to_string())
    s.to_csv(ROOT / "results/analysis/v6_cohort.csv")


if __name__ == "__main__":
    main()
