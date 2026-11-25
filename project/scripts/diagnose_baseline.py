#!/usr/bin/env python3
"""Decision D9 — diagnostic baseline (cycle 1, Phase 3). VALIDATION ONLY; test portions are never read.

LightGBM on hourly features. For each source hospital S in {A, B}: train on S-train, early-stop on S-val,
evaluate on S-val (internal) and T-val (external). Feature-group variants isolate where the
cross-hospital drop comes from. Every variant is appended to state/variants_tried.csv and written to
results/diagnosis/<variant>.json. Idempotent: variants with an existing result file are skipped.

Usage: python3 scripts/diagnose_baseline.py [--seed 0]
"""
import argparse
import csv
import json
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.data_physionet2019 import load  # noqa: E402
from src.features import build_features  # noqa: E402
from src.splits import make_splits  # noqa: E402
from src import stats as S  # noqa: E402

OUT = ROOT / "results" / "diagnosis"
FEAT_CACHE = ROOT / "data" / "processed" / "features_v1.parquet"
SPLIT_FILE = ROOT / "data" / "processed" / "splits_v1.csv"
PARAMS = dict(objective="binary", learning_rate=0.05, num_leaves=63, min_child_samples=100,
              feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0,
              num_threads=4, verbose=-1)


def features():
    if FEAT_CACHE.exists():
        feat = pd.read_parquet(FEAT_CACHE)
        groups = json.loads((FEAT_CACHE.with_suffix(".groups.json")).read_text())
    else:
        feat, groups = build_features(load())
        tmp = FEAT_CACHE.with_suffix(".tmp")
        feat.to_parquet(tmp)
        tmp.replace(FEAT_CACHE)
        FEAT_CACHE.with_suffix(".groups.json").write_text(json.dumps(groups))
    if SPLIT_FILE.exists():
        sp = pd.read_csv(SPLIT_FILE, dtype={"pid": str})
    else:
        sp = make_splits(feat)
        sp.to_csv(SPLIT_FILE, index=False)
    feat = feat.merge(sp[["pid", "split"]], on="pid", how="left")
    return feat, groups


def variant_cols(groups, name):
    allc = groups["value"] + groups["trend"] + groups["process"] + groups["context"]
    if name == "all":
        return allc
    if name == "no_process":
        return [c for c in allc if c not in groups["process"]]
    if name == "no_iculos":
        return [c for c in allc if c != "ICULOS"]
    if name == "no_process_no_iculos":
        return [c for c in allc if c not in groups["process"] and c != "ICULOS"]
    if name == "process_only":
        return groups["process"] + ["Age", "Gender"]
    if name == "vitals_only":  # vitals values + trends + demographics, no labs at all
        from src.data_physionet2019 import VITALS
        return [c for c in allc if (c.split("_")[0] in VITALS and c in groups["value"]) or c in groups["trend"]] + ["Age", "Gender"]
    raise ValueError(name)


def metrics(y, p):
    a, b, citl = S.calibration_slope_intercept(y, p)
    return dict(n_rows=int(len(y)), prevalence=float(np.mean(y)), mean_pred=float(np.mean(p)),
                auroc=S.auroc(y, p), auprc=S.auprc(y, p), brier=S.brier(y, p), cal_slope=b, citl=citl)


def patient_metrics(df, p):
    """Patient-level: max hourly risk vs ever-septic."""
    d = pd.DataFrame({"pid": df["pid"].values, "y": df["y"].values, "p": p}).groupby("pid").max()
    return dict(n_pat=int(len(d)), auroc=S.auroc(d.y, d.p), auprc=S.auprc(d.y, d.p))


def log_variant(vid, desc, evaluated_on, metric, value, notes):
    f = ROOT / "state" / "variants_tried.csv"
    with open(f, "a", newline="") as fh:
        csv.writer(fh).writerow([vid, 1, date.today().isoformat(), desc, vid, evaluated_on, metric,
                                 f"{value:.4f}", "diagnostic", notes])


def add_budget(seconds):
    f = ROOT / "state" / "budget.json"
    b = json.loads(f.read_text())
    b["per_cycle"]["1"] = b["per_cycle"].get("1", 0) + seconds
    b["global_seconds"] = b.get("global_seconds", 0) + seconds
    tmp = f.with_suffix(".tmp")
    tmp.write_text(json.dumps(b, indent=1))
    tmp.replace(f)


def main():
    import lightgbm as lgb
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--variants", default="all,no_process,no_iculos,no_process_no_iculos,process_only,vitals_only")
    args = ap.parse_args()
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    feat, groups = features()
    assert not (feat["split"] == "").any() and feat["split"].notna().all()
    for name in args.variants.split(","):
        cols = variant_cols(groups, name)
        for src, tgt in (("A", "B"), ("B", "A")):
            vid = f"diag_{name}_{src}2{tgt}_s{args.seed}"
            rf = OUT / f"{vid}.json"
            if rf.exists():
                print("skip", vid)
                continue
            t1 = time.time()
            tr = feat[(feat.hospital == src) & (feat.split == "train")]
            va = feat[(feat.hospital == src) & (feat.split == "val")]
            ex = feat[(feat.hospital == tgt) & (feat.split == "val")]
            dtr = lgb.Dataset(tr[cols], tr["y"], free_raw_data=True)
            dva = lgb.Dataset(va[cols], va["y"], reference=dtr)
            m = lgb.train({**PARAMS, "seed": args.seed}, dtr, num_boost_round=2000, valid_sets=[dva],
                          callbacks=[lgb.early_stopping(100, verbose=False)])
            pi, pe = m.predict(va[cols], num_iteration=m.best_iteration), m.predict(ex[cols], num_iteration=m.best_iteration)
            imp = pd.Series(m.feature_importance("gain"), index=cols).sort_values(ascending=False)
            res = dict(variant=vid, feature_set=name, source=src, target=tgt, seed=args.seed, n_features=len(cols),
                       best_iter=int(m.best_iteration), internal=metrics(va["y"].values, pi),
                       external=metrics(ex["y"].values, pe), internal_patient=patient_metrics(va, pi),
                       external_patient=patient_metrics(ex, pe),
                       top_gain=(imp.head(20) / imp.sum()).round(4).to_dict(), seconds=round(time.time() - t1, 1))
            np.save(OUT / f"{vid}_pred_int.npy", pi.astype(np.float32))
            np.save(OUT / f"{vid}_pred_ext.npy", pe.astype(np.float32))
            tmp = rf.with_suffix(".tmp")
            tmp.write_text(json.dumps(res, indent=1))
            tmp.replace(rf)
            log_variant(vid, f"LightGBM {name} train {src} -> {src}-val", f"{src}-val", "auroc_hourly", res["internal"]["auroc"], "")
            log_variant(vid, f"LightGBM {name} train {src} -> {tgt}-val", f"{tgt}-val", "auroc_hourly", res["external"]["auroc"], "")
            print(f"{vid}: int {res['internal']['auroc']:.3f} ext {res['external']['auroc']:.3f} "
                  f"(pat {res['internal_patient']['auroc']:.3f}/{res['external_patient']['auroc']:.3f}) it={m.best_iteration}", flush=True)
    add_budget(time.time() - t0)


if __name__ == "__main__":
    main()
