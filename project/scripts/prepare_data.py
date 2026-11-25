#!/usr/bin/env python3
"""Rebuild the git-ignored processed caches after a fresh clone / new container. Idempotent.

Produces (same code paths as the original builders, so outputs are identical):
  data/processed/physionet2019.parquet      (src.data_physionet2019.load)
  data/processed/features_v1.parquet (+ .groups.json), data/processed/splits_v1.csv
                                            (scripts/diagnose_baseline.features)
  data/processed/features_harm_v1.parquet   (same harmonisation as scripts/proto_harmonise.py)
Prints an MD5 of splits_v1.csv; expected 0883ae5b4726bdc6fbe0c41bbc4f7d6d (D19).
"""
import hashlib
import importlib.util
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_physionet2019 import load  # noqa: E402
from src.features import build_features  # noqa: E402

spec = importlib.util.spec_from_file_location("db", ROOT / "scripts/diagnose_baseline.py")
db = importlib.util.module_from_spec(spec)
spec.loader.exec_module(db)

# The split is PINNED in git (configs/splits_v1.csv, decision D19): copy it before anything else so
# the rule-based regeneration in diagnose_baseline.features() is never used for experiments.
pinned = ROOT / "configs/splits_v1.csv"
target = ROOT / "data/processed/splits_v1.csv"
target.parent.mkdir(parents=True, exist_ok=True)
if not target.exists() or target.read_bytes() != pinned.read_bytes():
    target.write_bytes(pinned.read_bytes())
db.features()  # builds features_v1 + groups if missing (split already in place)
harm = ROOT / "data/processed/features_harm_v1.parquet"
if not harm.exists():
    raw = load()
    raw.loc[raw.Calcium < 2, "Calcium"] = np.nan
    raw["Age"] = np.floor(raw["Age"])
    feat, _ = build_features(raw)
    tmp = harm.with_suffix(".tmp")
    feat.to_parquet(tmp)
    tmp.replace(harm)
sp = ROOT / "data/processed/splits_v1.csv"
print("splits_v1.csv md5", hashlib.md5(sp.read_bytes()).hexdigest())
