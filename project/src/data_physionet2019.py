"""Load PhysioNet/CinC 2019 sepsis challenge training data (hospital systems A and B) into one table.
Idempotent: caches to data/processed/physionet2019.parquet."""
from pathlib import Path
import numpy as np
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "physionet2019"
CACHE = ROOT / "data" / "processed" / "physionet2019.parquet"
VITALS = ["HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp", "EtCO2"]
LABS = ["BaseExcess", "HCO3", "FiO2", "pH", "PaCO2", "SaO2", "AST", "BUN", "Alkalinephos", "Calcium", "Chloride",
        "Creatinine", "Bilirubin_direct", "Glucose", "Lactate", "Magnesium", "Phosphate", "Potassium", "Bilirubin_total",
        "TroponinI", "Hct", "Hgb", "PTT", "WBC", "Fibrinogen", "Platelets"]
DEMO = ["Age", "Gender", "Unit1", "Unit2", "HospAdmTime", "ICULOS"]


def build(expected=(20336, 20000)):
    frames = []
    for s, n_exp in zip("AB", expected):
        files = sorted((RAW / f"training_set{s}").glob("p*.psv"))
        if len(files) != n_exp:
            raise RuntimeError(f"set {s}: found {len(files)} files, expected {n_exp}; run scripts/download_physionet2019.sh")
        for f in files:
            d = pd.read_csv(f, sep="|")
            d.insert(0, "pid", f.stem)
            d.insert(1, "hospital", s)
            frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    for c in df.columns[2:]:
        df[c] = df[c].astype("float32")
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    tmp = CACHE.with_suffix(".tmp")
    df.to_parquet(tmp)
    tmp.replace(CACHE)
    return df


def load():
    if CACHE.exists():
        return pd.read_parquet(CACHE)
    return build()
