#!/usr/bin/env python3
"""Cohort counts cited in the manuscript (writes results/cohort_counts.json). Idempotent."""
import json, sys
from pathlib import Path
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from src.train_eval import load_cells
raw = pd.read_parquet(ROOT / "data/processed/physionet2019.parquet", columns=["pid", "hospital"])
st = raw.groupby("pid").hospital.first()
f, cols = load_cells("none")
p = f.groupby("pid").agg(cell=("cell", "first"), split=("split", "first"), sep=("y", "max"), n=("y", "size"))
out = dict(stays_total=int(len(st)), stays_A=int((st == "A").sum()), stays_B=int((st == "B").sum()), hourly_rows_total=int(len(raw)),
           cell_stays=int(len(p)), cell_patient_hours=int(p.n.sum()), cell_septic_stays=int(p.sep.sum()), n_features=len(cols),
           test_patients={c: int(v) for c, v in p[p.split == "test"].groupby("cell").size().items()},
           test_septic={c: int(v) for c, v in p[p.split == "test"].groupby("cell").sep.sum().items()})
(ROOT / "results/cohort_counts.json").write_text(json.dumps(out, indent=1)); print(json.dumps(out))
