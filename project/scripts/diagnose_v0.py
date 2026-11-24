#!/usr/bin/env python3
"""Diagnostic baseline (decision D9, Section 6.4 rung 1). Uses TRAIN and VAL splits only; never TEST.

For each source hospital S in {A, B} and feature-set variant V:
  train LightGBM on S-train (early stopping on S-val), evaluate on S-val (internal) and T-val (external).
Variants: full, no_process, no_ICULOS, no_process_no_ICULOS, value_only, process_only.
Writes results/diagnostic/diag_v0.json and appends rows to state/variants_tried.csv.
Idempotent: skips variants already present in the output file.
"""
import json, sys, time, csv
from pathlib import Path
import numpy as np
import pandas as pd
import lightgbm as lgb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_physionet2019 import load
from src.features import build_features
from src.splits import make_splits
from src import stats as S

OUT = ROOT / "results" / "diagnostic" / "diag_v0.json"
FEAT_CACHE = ROOT / "data" / "processed" / "features_v0.parquet"
PARAMS = dict(objective="binary", learning_rate=0.05, num_leaves=63, min_data_in_leaf=200,
              feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0,
              verbose=-1, num_threads=4, seed=0)


def get_features():
    if FEAT_CACHE.exists():
        feat = pd.read_parquet(FEAT_CACHE)
        groups = json.loads((FEAT_CACHE.with_suffix(".groups.json")).read_text())
        return feat, groups
    feat, groups = build_features(load())
    FEAT_CACHE.parent.mkdir(parents=True, exist_ok=True)
    feat.to_parquet(FEAT_CACHE)
    FEAT_CACHE.with_suffix(".groups.json").write_text(json.dumps(groups))
    return feat, groups


def variant_cols(groups, v):
    allc = groups["value"] + groups["trend"] + groups["process"] + groups["context"]
    if v == "full":
        return allc
    if v == "no_process":
        return [c for c in allc if c not in groups["process"]]
    if v == "no_ICULOS":
        return [c for c in allc if c != "ICULOS"]
    if v == "no_process_no_ICULOS":
        return [c for c in allc if c not in groups["process"] and c != "ICULOS"]
    if v == "value_only":
        return groups["value"] + groups["trend"] + [c for c in groups["context"] if c != "ICULOS"]
    if v == "process_only":
        return groups["process"] + ["ICULOS"]
    raise ValueError(v)


def evaluate(y, p, pid):
    a, b, citl = S.calibration_slope_intercept(y, p)
    # patient-level: max risk over stay vs ever-septic
    d = pd.DataFrame({"pid": pid, "y": y, "p": p}).groupby("pid").max()
    return {"auroc": S.auroc(y, p), "auprc": S.auprc(y, p), "brier": S.brier(y, p),
            "cal_intercept": a, "cal_slope": b, "citl": citl, "prev": float(np.mean(y)),
            "mean_p": float(np.mean(p)), "patient_auroc": S.auroc(d.y.values, d.p.values), "n_rows": int(len(y))}


def main():
    t0 = time.time()
    feat, groups = get_features()
    sp = make_splits(feat)
    feat = feat.merge(sp[["pid", "split"]], on="pid", how="left")
    print(f"features ready {feat.shape} in {time.time()-t0:.0f}s", flush=True)
    res = json.loads(OUT.read_text()) if OUT.exists() else {}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    variants = ["full", "no_process", "no_ICULOS", "no_process_no_ICULOS", "value_only", "process_only"]
    for src in "AB":
        tgt = "B" if src == "A" else "A"
        tr = feat[(feat.hospital == src) & (feat.split == "train")]
        va = feat[(feat.hospital == src) & (feat.split == "val")]
        tv = feat[(feat.hospital == tgt) & (feat.split == "val")]
        for v in variants:
            key = f"{src}->{tgt}:{v}"
            if key in res:
                continue
            cols = variant_cols(groups, v)
            t1 = time.time()
            dtr = lgb.Dataset(tr[cols], tr.y)
            dva = lgb.Dataset(va[cols], va.y, reference=dtr)
            m = lgb.train(PARAMS, dtr, 2000, valid_sets=[dva],
                          callbacks=[lgb.early_stopping(100, verbose=False)])
            r = {"variant": v, "source": src, "target": tgt, "n_features": len(cols),
                 "best_iter": m.best_iteration,
                 "internal_val": evaluate(va.y.values, m.predict(va[cols], num_iteration=m.best_iteration), va.pid.values),
                 "external_val": evaluate(tv.y.values, m.predict(tv[cols], num_iteration=m.best_iteration), tv.pid.values)}
            imp = pd.Series(m.feature_importance("gain"), index=cols)
            r["top_gain"] = (imp / imp.sum()).sort_values(ascending=False).head(15).round(4).to_dict()
            r["gain_share_by_group"] = {g: float((imp.reindex([c for c in gl if c in cols]).sum()) / imp.sum())
                                         for g, gl in groups.items()}
            r["seconds"] = time.time() - t1
            res[key] = r
            tmp = OUT.with_suffix(".tmp"); tmp.write_text(json.dumps(res, indent=1)); tmp.replace(OUT)
            iv, ev = r["internal_val"], r["external_val"]
            print(f"{key}: int AUROC {iv['auroc']:.4f} ext AUROC {ev['auroc']:.4f} | int AUPRC {iv['auprc']:.4f} "
                  f"ext AUPRC {ev['auprc']:.4f} | ext slope {ev['cal_slope']:.2f} citl {ev['citl']:.2f} "
                  f"({r['seconds']:.0f}s)", flush=True)
            with open(ROOT / "state" / "variants_tried.csv", "a", newline="") as f:
                w = csv.writer(f)
                w.writerow([f"diag0_{src}{tgt}_{v}", 1, time.strftime("%Y-%m-%d"),
                            f"diagnostic LightGBM {src}->{tgt} feature set {v}", "diag_v0", "val (internal+external)",
                            "hourly AUROC int/ext", f"{iv['auroc']:.4f}/{ev['auroc']:.4f}", "diagnostic", ""])
    print("ALL DONE", time.time() - t0)


if __name__ == "__main__":
    main()
