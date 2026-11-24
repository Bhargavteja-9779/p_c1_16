#!/usr/bin/env python3
"""G8 data-leakage check (cycle 1). Read-only; writes results/leakage_check.json. Idempotent.

Checks
 1. split integrity: every patient in exactly one split; no patient in two cells; pinned split md5 (D19).
 2. duplicate patients: identical raw time series under two different pids (within or across hospitals).
 3. no look-ahead in features: for a random sample of patients, truncating the record at hour t and rebuilding
    gives exactly the same feature row at t as the full build.
 4. feature list excludes label / identifiers / unit / hospital.
 5. fitting scope (code assertions on src/train_eval.py): models fit on source-train only, model selection on
    source-val only, LR preprocessing statistics from source-train only, quantile normalisation from train rows.
"""
import hashlib, inspect, json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_physionet2019 import load
from src.features import build_features
from src import train_eval as TE

out = {}
sp = pd.read_csv(ROOT / "data/processed/splits_v1.csv", dtype={"pid": str})
out["split_md5"] = hashlib.md5((ROOT / "data/processed/splits_v1.csv").read_bytes()).hexdigest()
out["split_md5_matches_pinned"] = out["split_md5"] == hashlib.md5((ROOT / "configs/splits_v1.csv").read_bytes()).hexdigest()
out["pid_unique_in_split_file"] = bool(sp.pid.is_unique)
feat, cols = TE.load_cells("none")
pc = feat.groupby("pid").agg(ns=("split", "nunique"), nc=("cell", "nunique"))
out["patients_in_cells"] = int(len(pc))
out["patients_in_>1_split"] = int((pc.ns > 1).sum())
out["patients_in_>1_cell"] = int((pc.nc > 1).sum())

raw = load()
vals = [c for c in raw.columns if c not in ("pid", "hospital")]
h = raw.groupby("pid", sort=False)[vals].apply(lambda d: hashlib.md5(d.to_numpy(dtype="float64", na_value=-999).tobytes()).hexdigest())
dup = h[h.duplicated(keep=False)]
out["duplicate_patient_series"] = int(dup.duplicated().sum())
out["duplicate_examples"] = dup.sort_values().head(10).index.tolist()

rng = np.random.default_rng(0)
pids = rng.choice(raw.pid.unique(), 200, replace=False)
sub = raw[raw.pid.isin(pids)]
full, groups = build_features(sub)
allc = groups["value"] + groups["trend"] + groups["process"] + groups["context"]
mism = 0; checked = 0
for p in pids[:200]:
    d = sub[sub.pid == p]
    if len(d) < 3: continue
    t = int(rng.integers(1, len(d)))
    tr, _ = build_features(d.iloc[:t])
    a = tr[allc].iloc[-1].to_numpy(dtype=float)
    b = full[full.pid == p][allc].iloc[t - 1].to_numpy(dtype=float)
    checked += 1
    mism += int(not np.allclose(a, b, equal_nan=True, rtol=1e-5, atol=1e-6))
out["lookahead_patients_checked"] = checked
out["lookahead_mismatches"] = mism

forbidden = {"y", "SepsisLabel", "pid", "hospital", "unit", "cell", "split", "Unit1", "Unit2", "ICULOS_raw"}
out["forbidden_features_used"] = sorted(forbidden & set(cols))

src = inspect.getsource(TE)
out["code_assertions"] = {
    "train_rows_from_source_train_only": 'tr = feat[(feat.cell == a.train_cell) & (feat.split == "train")]' in src,
    "selection_on_source_val_only": 'va = feat[(feat.cell == a.train_cell) & (feat.split == "val")]' in src,
    "lr_preprocessing_from_train": "med = tr[cols].median()" in src and "lo, hi = tr[cols].quantile" in src,
    "quantile_norm_reference_train_rows": 'ref = feat.loc[m & (feat.split == "train")]' in src,
}
out["notes"] = ("Quantile normalisation (harm_noproc_norm) uses UNLABELLED train-split rows of both hospitals, "
                "by design (unlabelled site fix); no test rows and no target labels are used. "
                "Split history: journal 011 / D19 (B split reconstructed and pinned).")
ok = (out["split_md5_matches_pinned"] and out["pid_unique_in_split_file"] and out["patients_in_>1_split"] == 0
      and out["patients_in_>1_cell"] == 0 and out["duplicate_patient_series"] == 0 and out["lookahead_mismatches"] == 0
      and not out["forbidden_features_used"] and all(out["code_assertions"].values()))
out["PASS"] = bool(ok)
(ROOT / "results/leakage_check.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
