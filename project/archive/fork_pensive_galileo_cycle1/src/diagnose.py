"""Decision D9 diagnostic baseline (cycle 1, Phase 3). VALIDATION ONLY — test portions are never read here.

LightGBM with FIXED hyperparameters (no tuning; this is a diagnosis, not a result) trained on
source-train, early-stopped on source-val, evaluated on source-val and target-val (A->B and B->A),
for feature-set variants that drop the measurement-process group and/or ICULOS.

Metrics (hour level, utility-free): AUROC, AUPRC; patient level: AUROC of max-over-stay score
vs ever-septic. Every variant is appended to state/variants_tried.csv and results/diagnosis/*.json.

Usage: python -m src.diagnose [--seed 0]
"""
import argparse
import csv
import json
import time
from datetime import date
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score, roc_auc_score

from .data_physionet2019 import load
from .features import build_features
from .splits import make_splits

ROOT = Path(__file__).resolve().parents[1]
FEAT_CACHE = ROOT / "data" / "processed" / "features_v1.parquet"
OUT = ROOT / "results" / "diagnosis"
PARAMS = dict(objective="binary", learning_rate=0.05, num_leaves=63, min_child_samples=100,
              feature_fraction=0.8, bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0,
              n_jobs=4, verbose=-1)


def get_features():
    if FEAT_CACHE.exists():
        feat = pd.read_parquet(FEAT_CACHE)
        groups = json.loads((FEAT_CACHE.with_suffix(".groups.json")).read_text())
        return feat, groups
    feat, groups = build_features(load())
    tmp = FEAT_CACHE.with_suffix(".tmp")
    feat.to_parquet(tmp)
    tmp.replace(FEAT_CACHE)
    FEAT_CACHE.with_suffix(".groups.json").write_text(json.dumps(groups))
    return feat, groups


def feature_sets(groups):
    base = groups["value"] + groups["trend"]
    ctx = groups["context"]
    noiculos = [c for c in ctx if c != "ICULOS"]
    return {
        "full": base + groups["process"] + ctx,
        "no_process": base + ctx,
        "no_iculos": base + groups["process"] + noiculos,
        "no_process_no_iculos": base + noiculos,
        "iculos_only": ["ICULOS"],
        "process_only": groups["process"] + ["ICULOS"],
    }


def evaluate(y, p, pid):
    d = pd.DataFrame({"y": y, "p": p, "pid": pid}).groupby("pid").max()
    return {"auroc_hour": float(roc_auc_score(y, p)), "auprc_hour": float(average_precision_score(y, p)),
            "prev_hour": float(np.mean(y)), "auroc_patient": float(roc_auc_score(d["y"], d["p"])),
            "auprc_patient": float(average_precision_score(d["y"], d["p"])), "n_patients": int(len(d))}


def log_variant(row):
    path = ROOT / "state" / "variants_tried.csv"
    new = not path.exists() or path.stat().st_size == 0
    with open(path, "a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["variant_id", "cycle", "date", "description", "config_id", "evaluated_on", "metric", "value",
                        "outcome", "notes"])
        w.writerow(row)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    feat, groups = get_features()
    sp = make_splits(feat)
    sp.to_csv(OUT / "splits_patients.csv", index=False)
    feat = feat.merge(sp[["pid", "split"]], on="pid", how="left")
    assert feat["split"].notna().all()
    fsets = feature_sets(groups)
    for src in "AB":
        tgt = "B" if src == "A" else "A"
        tr = feat[(feat.hospital == src) & (feat.split == "train")]
        va = feat[(feat.hospital == src) & (feat.split == "val")]
        tv = feat[(feat.hospital == tgt) & (feat.split == "val")]
        for name, cols in fsets.items():
            cid = f"diag_lgb_{name}_{src}_s{args.seed}"
            fout = OUT / f"{cid}.json"
            if fout.exists():
                continue
            t0 = time.time()
            params = dict(PARAMS, seed=args.seed)
            dtr = lgb.Dataset(tr[cols], tr["y"])
            dva = lgb.Dataset(va[cols], va["y"], reference=dtr)
            m = lgb.train(params, dtr, num_boost_round=2000, valid_sets=[dva],
                          callbacks=[lgb.early_stopping(50, verbose=False)])
            res = {"config_id": cid, "source": src, "target": tgt, "feature_set": name, "n_features": len(cols),
                   "seed": args.seed, "best_iter": m.best_iteration, "params": params,
                   "source_val": evaluate(va["y"].values, m.predict(va[cols], num_iteration=m.best_iteration), va["pid"].values),
                   "target_val": evaluate(tv["y"].values, m.predict(tv[cols], num_iteration=m.best_iteration), tv["pid"].values),
                   "seconds": round(time.time() - t0, 1)}
            imp = pd.Series(m.feature_importance("gain"), index=cols).sort_values(ascending=False)
            res["top_gain"] = {k: float(v) for k, v in (imp / imp.sum()).head(15).items()}
            tmp = fout.with_suffix(".tmp")
            tmp.write_text(json.dumps(res, indent=2))
            tmp.replace(fout)
            for where in ["source_val", "target_val"]:
                log_variant([cid + "_" + where, 1, date.today().isoformat(), f"D9 diagnostic LightGBM {name} trained on {src}",
                             cid, f"{src if where == 'source_val' else tgt}-val", "auroc_hour",
                             round(res[where]["auroc_hour"], 4), "diagnostic", f"patient AUROC {res[where]['auroc_patient']:.4f}"])
            print(cid, f"src {res['source_val']['auroc_hour']:.4f} tgt {res['target_val']['auroc_hour']:.4f}",
                  f"iters {m.best_iteration} {res['seconds']}s", flush=True)


if __name__ == "__main__":
    main()
