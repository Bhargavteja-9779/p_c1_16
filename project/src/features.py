"""Hourly feature construction for dynamic ICU prediction (PhysioNet 2019 format).

For each patient-hour t we use only data at times <= t (no look-ahead):
  * value features: last observed value (forward fill within patient), NaN if never observed
  * vital-sign trend features: rolling mean / min / max over last 6 h, and difference vs 6 h ago
  * measurement-process features ("practice" features): hours since last observation and
    number of observations in the last 24 h, per variable
  * demographics/context: Age, Gender, ICULOS, HospAdmTime (Unit1/Unit2 kept only as group labels)
Feature groups are returned so experiments can drop groups (ablations).
"""
import numpy as np
import pandas as pd
from .data_physionet2019 import VITALS, LABS

CORE_VITALS = ["HR", "O2Sat", "Temp", "SBP", "MAP", "DBP", "Resp"]
VARS = VITALS + LABS


def build_features(df):
    df = df.sort_values(["pid", "ICULOS"], kind="stable").reset_index(drop=True)
    g = df.groupby("pid", sort=False)
    out = {"pid": df["pid"].values, "hospital": df["hospital"].values, "y": df["SepsisLabel"].values.astype(np.int8),
           "unit": np.where(df["Unit1"] == 1, "MICU", np.where(df["Unit2"] == 1, "SICU", "UNK")),
           "ICULOS_raw": df["ICULOS"].values}
    groups = {"value": [], "trend": [], "process": [], "context": []}
    obs = df[VARS].notna()
    # step index within patient
    step = g.cumcount().values
    for v in VARS:
        ff = g[v].ffill()
        out[f"{v}_last"] = ff.values.astype(np.float32)
        groups["value"].append(f"{v}_last")
        # hours since last observation
        o = obs[v].values
        last_idx = pd.Series(np.where(o, step, np.nan)).groupby(df["pid"].values, sort=False).ffill().values
        hs = (step - last_idx).astype(np.float32)
        out[f"{v}_hsince"] = hs
        cnt = obs[v].astype(np.float32).groupby(df["pid"].values, sort=False).rolling(24, min_periods=1).sum().values
        out[f"{v}_n24"] = cnt.astype(np.float32)
        groups["process"] += [f"{v}_hsince", f"{v}_n24"]
    for v in CORE_VITALS:
        ff = pd.Series(out[f"{v}_last"])
        r = ff.groupby(df["pid"].values, sort=False).rolling(6, min_periods=1)
        out[f"{v}_mean6"] = r.mean().values.astype(np.float32)
        out[f"{v}_min6"] = r.min().values.astype(np.float32)
        out[f"{v}_max6"] = r.max().values.astype(np.float32)
        out[f"{v}_d6"] = (ff - ff.groupby(df["pid"].values, sort=False).shift(6)).values.astype(np.float32)
        groups["trend"] += [f"{v}_mean6", f"{v}_min6", f"{v}_max6", f"{v}_d6"]
    for c in ["Age", "Gender", "ICULOS", "HospAdmTime"]:
        out[c] = df[c].values.astype(np.float32)
        groups["context"].append(c)
    return pd.DataFrame(out), groups
