"""Fixed patient-level splits (decided before any modelling; never changed after seeing results).

Within each hospital: patients are split 60/20/20 into train/val/test, stratified by whether the
patient ever has SepsisLabel=1. SPLIT_SEED is fixed and independent of model seeds.
Cross-hospital protocol: train on source-train, select on source-val, report on target-test.
The test portions are only used by frozen confirmation runs (E6) and the final report.
"""
import numpy as np
import pandas as pd

SPLIT_SEED = 2026


def make_splits(feat):
    pat = feat.groupby("pid").agg(hospital=("hospital", "first"), sep=("y", "max")).reset_index()
    rng = np.random.default_rng(SPLIT_SEED)
    pat["split"] = ""
    for (h, s), idx in pat.groupby(["hospital", "sep"]).groups.items():
        idx = np.array(sorted(idx))
        rng.shuffle(idx)
        n = len(idx)
        a, b = int(0.6 * n), int(0.8 * n)
        pat.loc[idx[:a], "split"] = "train"
        pat.loc[idx[a:b], "split"] = "val"
        pat.loc[idx[b:], "split"] = "test"
    return pat[["pid", "hospital", "sep", "split"]]
