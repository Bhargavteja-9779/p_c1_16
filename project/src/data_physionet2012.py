"""PhysioNet/CinC 2012 challenge (MIMIC-II, 12,000 ICU stays, first 48 h; ODC-By 1.0) -> hourly table in the
PhysioNet 2019 column convention, so the same feature code can be used (plan_v6).

Hour index: ICULOS = floor(minutes since ICU admission / 60) + 1 (same convention as 2019: first row ICULOS 1).
Multiple measurements within an hour are averaged. Blood pressure: invasive value if recorded in that hour,
otherwise the non-invasive value (decided before looking at outcomes; recorded in plan_v6).
Unit: ICUType 3 = MICU, 4 = SICU, 1 = CCU, 2 = CSRU.
Cached to data/processed/physionet2012.parquet. Idempotent.
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "physionet2012"
CACHE = ROOT / "data" / "processed" / "physionet2012.parquet"
MAP2019 = {"HR": "HR", "Temp": "Temp", "RespRate": "Resp", "FiO2": "FiO2", "pH": "pH", "PaCO2": "PaCO2", "SaO2": "SaO2",
           "AST": "AST", "BUN": "BUN", "ALP": "Alkalinephos", "Creatinine": "Creatinine", "Glucose": "Glucose",
           "Lactate": "Lactate", "Mg": "Magnesium", "K": "Potassium", "Bilirubin": "Bilirubin_total",
           "TroponinI": "TroponinI", "HCT": "Hct", "Platelets": "Platelets", "WBC": "WBC", "HCO3": "HCO3"}
BP = {"SBP": ("SysABP", "NISysABP"), "MAP": ("MAP", "NIMAP"), "DBP": ("DiasABP", "NIDiasABP")}
UNIT = {1: "CCU", 2: "CSRU", 3: "MICU", 4: "SICU"}


def _one(path):
    d = pd.read_csv(path)
    d = d[d.Parameter.notna()]
    desc = d[d.Time == "00:00"].set_index("Parameter")["Value"]
    rid = str(int(desc["RecordID"]))
    mins = d.Time.str.split(":", expand=True).astype(int)
    d = d.assign(h=(mins[0] * 60 + mins[1]) // 60 + 1)
    ts = d[~d.Parameter.isin(["RecordID", "Age", "Gender", "Height", "ICUType", "Weight"]) | (d.Time != "00:00")]
    ts = ts[ts.Value >= 0]  # -1 = missing in this dataset
    wide = ts.pivot_table(index="h", columns="Parameter", values="Value", aggfunc="mean")
    out = pd.DataFrame(index=pd.RangeIndex(1, 49, name="ICULOS"))
    for k, v in MAP2019.items():
        out[v] = wide[k] if k in wide else np.nan
    for v, (inv, ni) in BP.items():
        a = wide[inv] if inv in wide else pd.Series(np.nan, index=wide.index)
        b = wide[ni] if ni in wide else pd.Series(np.nan, index=wide.index)
        out[v] = a.where(a.notna() & (a > 0), b)
    out = out.reset_index()
    out.insert(0, "pid", "m" + rid)
    out["Age"] = float(desc.get("Age", np.nan))
    out["Gender"] = float(desc.get("Gender", np.nan))
    out["unit"] = UNIT.get(int(desc.get("ICUType", 0)), "UNK")
    return out


def load():
    if CACHE.exists():
        return pd.read_parquet(CACHE)
    frames = [_one(p) for s in "abc" for p in sorted((RAW / f"set-{s}").glob("*.txt"))]
    df = pd.concat(frames, ignore_index=True)
    for c in df.columns:
        if c not in ("pid", "unit"):
            df[c] = df[c].astype("float32")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    tmp = CACHE.with_suffix(".tmp")
    df.to_parquet(tmp)
    tmp.replace(CACHE)
    return df
