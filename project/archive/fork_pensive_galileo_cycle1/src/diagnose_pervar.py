"""Per-variable decomposition of the measurement-process effect (cycle 1, diagnostic; VALIDATION ONLY).

Base model: value + trend + context WITHOUT ICULOS (decision D13: ICULOS excluded because septic
records are truncated at onset+3h, journal 007). For each variable v, add only v's process features
(v_hsince, v_n24) and measure the change in source-val and target-val hour AUROC versus the base.

Label-free policy-shift scores per variable (use only measurement indicators, never sepsis labels):
  * rate_logratio: log(measurement rate in target / in source) over all hours
  * policy_auc_src / policy_auc_tgt: a LightGBM "measurement policy" model predicts whether v is
    measured at hour t from the patient state (value+trend+context features, no process features),
    trained on source-train; AUROC on source-val vs target-val (target used unlabelled).
Outputs results/diagnosis/pervar_<src>_s<seed>.csv
"""
import argparse
from pathlib import Path

import lightgbm as lgb
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

from .data_physionet2019 import VITALS, LABS
from .diagnose import PARAMS, get_features
from .splits import make_splits

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "diagnosis"


def fit_auc(tr, va, tv, cols, ycol, seed, rounds=2000):
    p = dict(PARAMS, seed=seed)
    dtr = lgb.Dataset(tr[cols], tr[ycol])
    dva = lgb.Dataset(va[cols], va[ycol], reference=dtr)
    m = lgb.train(p, dtr, num_boost_round=rounds, valid_sets=[dva], callbacks=[lgb.early_stopping(50, verbose=False)])
    a = roc_auc_score(va[ycol], m.predict(va[cols], num_iteration=m.best_iteration))
    b = roc_auc_score(tv[ycol], m.predict(tv[cols], num_iteration=m.best_iteration))
    return a, b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--policy_subsample", type=int, default=300000)
    args = ap.parse_args()
    feat, groups = get_features()
    sp = make_splits(feat)
    feat = feat.merge(sp[["pid", "split"]], on="pid", how="left")
    base = groups["value"] + groups["trend"] + [c for c in groups["context"] if c != "ICULOS"]
    rng = np.random.default_rng(args.seed)
    for src in "AB":
        out = OUT / f"pervar_{src}_s{args.seed}.csv"
        if out.exists():
            continue
        tgt = "B" if src == "A" else "A"
        tr = feat[(feat.hospital == src) & (feat.split == "train")]
        va = feat[(feat.hospital == src) & (feat.split == "val")]
        tv = feat[(feat.hospital == tgt) & (feat.split == "val")]
        b_src, b_tgt = fit_auc(tr, va, tv, base, "y", args.seed)
        rows = []
        for v in VITALS + LABS:
            pc = [f"{v}_hsince", f"{v}_n24"]
            s, t = fit_auc(tr, va, tv, base + pc, "y", args.seed)
            obs_s = (feat.loc[feat.hospital == src, f"{v}_hsince"] == 0).mean()
            obs_t = (feat.loc[feat.hospital == tgt, f"{v}_hsince"] == 0).mean()
            row = {"var": v, "kind": "vital" if v in VITALS else "lab", "src": src, "tgt": tgt, "seed": args.seed,
                   "base_src": b_src, "base_tgt": b_tgt, "d_src": s - b_src, "d_tgt": t - b_tgt,
                   "rate_src": obs_s, "rate_tgt": obs_t,
                   "rate_logratio": float(np.log((obs_t + 1e-6) / (obs_s + 1e-6)))}
            if obs_s > 0.001 and obs_t > 0.001:
                for d in (tr, va, tv):
                    d.loc[:, "_m"] = (d[f"{v}_hsince"] == 0).astype(np.int8)
                pcols = [c for c in base if not c.startswith(v + "_")]
                sub = lambda d: d.iloc[rng.choice(len(d), min(len(d), args.policy_subsample), replace=False)]
                trs, vas, tvs = sub(tr), sub(va), sub(tv)
                if trs["_m"].nunique() == 2 and vas["_m"].nunique() == 2 and tvs["_m"].nunique() == 2:
                    row["policy_auc_src"], row["policy_auc_tgt"] = fit_auc(trs, vas, tvs, pcols, "_m", args.seed, 500)
            rows.append(row)
            print(src, v, f"d_src {row['d_src']:+.4f} d_tgt {row['d_tgt']:+.4f} rate {obs_s:.3f}->{obs_t:.3f}",
                  f"policy {row.get('policy_auc_src', np.nan):.3f}->{row.get('policy_auc_tgt', np.nan):.3f}", flush=True)
        df = pd.DataFrame(rows)
        tmp = out.with_suffix(".tmp")
        df.to_csv(tmp, index=False)
        tmp.replace(out)


if __name__ == "__main__":
    main()
