#!/usr/bin/env python3
"""plan_v7 job: few-label repair of an imported model (task x source cell x target cell x seed; all n and methods).
See experiments/plan_v7.yaml. Writes results/v7/<job_id>.json (+ preds npz). Idempotent; source models cached in
checkpoints/v7/.
Usage: python3 scripts/adapt_v7.py --task T1 --source A_MICU --target B_MICU --seed 0 --split val
"""
import argparse, json, os, sys, time
from pathlib import Path
import numpy as np, pandas as pd
import lightgbm as lgb
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.train_eval import LGBM_BASE, LGBM_GRID
from src import stats as S

NS = [50, 100, 200, 400]
ROUNDS = [25, 50, 100, 200, 400]
RP = dict(objective="binary", learning_rate=0.05, num_leaves=7, min_child_samples=20, lambda_l2=10.0,
          feature_fraction=1.0, num_threads=int(os.environ.get("OMP_NUM_THREADS", 2)), verbose=-1)
METHODS = ["source", "local", "pooled", "resid_all", "spru", "resid_phys", "resid_rand"]


def load_task(task):
    if task == "T1":
        from src.train_eval import load_cells
        feat, cols = load_cells("none")
        groups = json.loads((ROOT / "data/processed/features_v1.groups.json").read_text())
    else:
        feat = pd.read_parquet(ROOT / "data/processed/features_v6.parquet")
        groups = json.loads((ROOT / "data/processed/features_v6.groups.json").read_text())
        cols = groups["value"] + groups["trend"] + groups["process"] + groups["context"]
    g = {k: [c for c in v if c in cols] for k, v in groups.items()}
    return feat, cols, g


def source_model(task, src, seed, feat, cols):
    ck = ROOT / "checkpoints/v7" / f"{task}_{src}_s{seed}.txt"
    if ck.exists():
        return lgb.Booster(model_file=str(ck))
    tr = feat[(feat.cell == src) & (feat.split == "train")]; va = feat[(feat.cell == src) & (feat.split == "val")]
    best = None
    for nl in LGBM_GRID:  # identical recipe to src/train_eval.fit_lgbm
        dtr = lgb.Dataset(tr[cols], tr.y)
        m = lgb.train({**LGBM_BASE, "num_leaves": nl, "seed": seed}, dtr, 3000,
                      valid_sets=[lgb.Dataset(va[cols], va.y, reference=dtr)], callbacks=[lgb.early_stopping(100, verbose=False)])
        a = S.auroc(va.y, m.predict(va[cols], num_iteration=m.best_iteration))
        if best is None or a > best[0]:
            best = (a, m)
    ck.parent.mkdir(parents=True, exist_ok=True)
    tmp = ck.with_suffix(".tmp"); best[1].save_model(str(tmp), num_iteration=best[1].best_iteration); tmp.replace(ck)
    return lgb.Booster(model_file=str(ck))


def sample_patients(tr, n, seed):
    pat = tr.groupby("pid").y.max()
    rng = np.random.default_rng(seed)
    pos, neg = pat[pat == 1].index.values, pat[pat == 0].index.values
    k = max(1, int(round(n * len(pos) / len(pat))))
    return np.concatenate([rng.choice(np.sort(pos), min(k, len(pos)), replace=False),
                           rng.choice(np.sort(neg), n - min(k, len(pos)), replace=False)])


def cv_rounds(X, y, pids, init, seed, w=None, extra=None):
    """Pick rounds from ROUNDS by 3-fold patient CV. extra=(Xs, ys, inits, ws) rows always added to training."""
    up = np.unique(pids); rng = np.random.default_rng(seed); rng.shuffle(up)
    folds = np.array_split(up, 3); score = np.zeros(len(ROUNDS)); used = 0
    for f in folds:
        te = np.isin(pids, f); trm = ~te
        if y[te].min() == y[te].max() or y[trm].min() == y[trm].max():
            continue
        Xt, yt, it = X[trm], y[trm], (init[trm] if init is not None else None)
        wt = w[trm] if w is not None else None
        if extra is not None:
            Xt = np.vstack([Xt, extra[0]]); yt = np.concatenate([yt, extra[1]]); wt = np.concatenate([wt, extra[3]])
            it = None
        m = lgb.train({**RP, "seed": seed}, lgb.Dataset(Xt, yt, init_score=it, weight=wt), max(ROUNDS))
        for i, r in enumerate(ROUNDS):
            p = m.predict(X[te], num_iteration=r, raw_score=True) + (init[te] if init is not None else 0)
            score[i] += S.auroc(y[te], p)
        used += 1
    return ROUNDS[int(np.argmax(score))] if used else 100


def fit_predict(Xl, yl, pl, init_l, Xe, init_e, seed, w=None, extra=None):
    r = cv_rounds(Xl, yl, pl, init_l, seed, w, extra)
    Xt, yt, it, wt = Xl, yl, init_l, w
    if extra is not None:
        Xt = np.vstack([Xl, extra[0]]); yt = np.concatenate([yl, extra[1]]); wt = np.concatenate([w, extra[3]]); it = None
    m = lgb.train({**RP, "seed": seed}, lgb.Dataset(Xt, yt, init_score=it, weight=wt), r)
    return m.predict(Xe, raw_score=True) + (init_e if init_e is not None else 0), r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--task", required=True); ap.add_argument("--source", required=True); ap.add_argument("--target", required=True)
    ap.add_argument("--seed", type=int, required=True); ap.add_argument("--split", required=True)
    a = ap.parse_args()
    jid = f"v7{'x' if a.split == 'val' else 'c'}__{a.task}__{a.source}__{a.target}__s{a.seed}__{a.split}"
    out = ROOT / "results/v7"; rf = out / f"{jid}.json"
    if rf.exists():
        print("exists"); return
    t0 = time.time()
    feat, cols, g = load_task(a.task)
    src = source_model(a.task, a.source, a.seed, feat, cols)
    sets = {"resid_all": cols, "spru": g["process"] + g["context"], "resid_phys": g["value"] + g["trend"]}
    rng = np.random.default_rng(a.seed)
    sets["resid_rand"] = list(rng.choice(cols, len(sets["spru"]), replace=False))
    tt = feat[(feat.cell == a.target) & (feat.split == "train")]
    ev = feat[(feat.cell == a.target) & (feat.split == a.split)]
    init_e = src.predict(ev[cols], raw_score=True)
    preds = {"pid": np.asarray(ev.pid.values, dtype="U12"), "y": ev.y.values.astype(np.int8), "source": init_e.astype(np.float32)}
    sel = {}
    srows = feat[(feat.cell == a.source) & (feat.split == "train")]
    for n in NS:
        pids = sample_patients(tt, n, a.seed * 1000 + n)
        L = tt[tt.pid.isin(pids)]
        yl, pl = L.y.values, L.pid.values
        init_l = src.predict(L[cols], raw_score=True)
        p, r = fit_predict(L[cols].values, yl, pl, None, ev[cols].values, None, a.seed)
        preds[f"{n}__local"] = p.astype(np.float32); sel[f"{n}__local"] = r
        w = np.full(len(L), min(20.0, len(srows) / max(1, len(L))))
        extra = (srows[cols].values, srows.y.values, None, np.ones(len(srows)))
        p, r = fit_predict(L[cols].values, yl, pl, None, ev[cols].values, None, a.seed, w=w, extra=extra)
        preds[f"{n}__pooled"] = p.astype(np.float32); sel[f"{n}__pooled"] = r
        for mname, fs in sets.items():
            p, r = fit_predict(L[fs].values, yl, pl, init_l, ev[fs].values, init_e, a.seed)
            preds[f"{n}__{mname}"] = p.astype(np.float32); sel[f"{n}__{mname}"] = r
    (out / "preds").mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out / "preds" / f"{jid}.npz", **preds)
    res = {"job_id": jid, "task": a.task, "source": a.source, "target": a.target, "seed": a.seed, "split": a.split,
           "rounds": sel, "n_spru_features": len(sets["spru"]), "seconds": round(time.time() - t0, 1),
           "auroc": {k: S.auroc(preds["y"], v) for k, v in preds.items() if k not in ("pid", "y")}}
    tmp = rf.with_suffix(".tmp"); tmp.write_text(json.dumps(res, indent=1)); tmp.replace(rf)
    print(jid, res["seconds"], "s")


if __name__ == "__main__":
    main()
