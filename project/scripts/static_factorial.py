#!/usr/bin/env python3
"""plan_v4 / H7: the factorial (hospital x within-hospital factor) on the static 12-h early-warning task.

Task (published protocol, reproduced in results/g4_reproduce.json): stays with >= 24 hourly records and no positive
SepsisLabel in hours 1-12; one prediction per stay at hour 12 from window summaries of hours 1-12; label = any
SepsisLabel = 1 after hour 12. Features identical to scripts/g4_reproduce.py.
Cells: unit (MICU/SICU from Unit1/Unit2, first known hour; unknown excluded) or route (D: HospAdmTime >= -24, L: later).
Fit on the source cell's train split, model selection on its val split, evaluate on every cell's eval split.
Analysis = frozen analyze_transport bootstrap (rows are stays, so the 'hour' level is the patient level here).

Usage: python3 scripts/static_factorial.py fit --phase explore|confirm
       python3 scripts/static_factorial.py analyse --phase explore|confirm [--nboot N]
Outputs: results/v4/preds/<job>.npz, results/v4/<job>.json, results/analysis/v4_<phase>.json, tables/v4_<phase>.md
Idempotent: existing job outputs are skipped.
"""
import argparse, json, sys, time
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / "scripts"))
from sklearn.metrics import roc_auc_score
LEVELS = {"unit": ("MICU", "SICU"), "route": ("D", "L")}
CACHE = ROOT / "data/processed/static12_v1.parquet"
OUT = ROOT / "results/v4"


def cells_of(f):
    return [f"{h}_{l}" for h in "AB" for l in LEVELS[f]]


def build():
    if CACHE.exists():
        return pd.read_parquet(CACHE)
    from src.data_physionet2019 import load, VITALS, LABS
    raw = load().sort_values(["pid", "ICULOS"])
    n = raw.groupby("pid").size(); early = raw[raw.ICULOS <= 12].groupby("pid").SepsisLabel.max()
    coh = n[n >= 24].index.intersection(early[early == 0].index)
    r = raw[raw.pid.isin(coh)]
    w = r[r.ICULOS <= 12]; later = r[r.ICULOS > 12].groupby("pid").SepsisLabel.max()
    V = VITALS + LABS
    agg = w.groupby("pid")[V].agg(["last", "mean", "min", "max", "count"])
    agg.columns = [f"{a}_{b}" for a, b in agg.columns]
    miss = pd.DataFrame({f"{v}_miss": (agg[f"{v}_count"] == 0).astype(np.int8) for v in V})
    X = pd.concat([agg, miss, w.groupby("pid")[["Age", "Gender", "HospAdmTime"]].first()], axis=1)
    X["y"] = later.reindex(X.index).astype(int); X["h"] = r.groupby("pid").hospital.first()
    u = r.assign(unit=np.where(r.Unit1 == 1, "MICU", np.where(r.Unit2 == 1, "SICU", None)))
    X["unit"] = u.dropna(subset=["unit"]).groupby("pid").unit.first().reindex(X.index)
    X["route"] = np.where(X.HospAdmTime.isna(), None, np.where(X.HospAdmTime >= -24, "D", "L"))
    sp = pd.read_csv(ROOT / "data/processed/splits_v1.csv", dtype={"pid": str}).set_index("pid").split
    X["split"] = sp.reindex(X.index)
    X.index.name = "pid"; X = X.reset_index()
    tmp = CACHE.with_suffix(".tmp"); X.to_parquet(tmp); tmp.replace(CACHE)
    return X


META = ("pid", "y", "h", "unit", "route", "split", "cell")


def fit_lgbm(tr, va, cols, seed):
    import lightgbm as lgb
    best = None
    for nl in (15, 63, 255):
        m = lgb.train(dict(objective="binary", learning_rate=0.05, num_leaves=nl, min_child_samples=50, feature_fraction=0.8,
                           bagging_fraction=0.8, bagging_freq=1, lambda_l2=1.0, verbose=-1, num_threads=4, seed=seed),
                      lgb.Dataset(tr[cols], tr.y), 3000, valid_sets=[lgb.Dataset(va[cols], va.y)],
                      callbacks=[lgb.early_stopping(100, verbose=False)])
        a = roc_auc_score(va.y, m.predict(va[cols], num_iteration=m.best_iteration))
        if best is None or a > best[0]:
            best = (a, m, nl)
    m = best[1]
    return (lambda d: m.predict(d[cols], num_iteration=m.best_iteration)), {"num_leaves": best[2], "val_auroc": best[0]}


def fit_lr(tr, va, cols, seed):
    import warnings; warnings.filterwarnings("ignore")
    from sklearn.linear_model import LogisticRegression
    med = tr[cols].median(); mu = tr[cols].fillna(med).mean(); sd = tr[cols].fillna(med).std() + 1e-6
    T = lambda d: ((d[cols].fillna(med) - mu) / sd).fillna(0).clip(-10, 10).values
    best = None
    for C in (0.01, 0.1, 1.0):
        m = LogisticRegression(penalty="elasticnet", l1_ratio=0.5, C=C, solver="saga", max_iter=2000, random_state=seed).fit(T(tr), tr.y)
        a = roc_auc_score(va.y, m.predict_proba(T(va))[:, 1])
        if best is None or a > best[0]:
            best = (a, m, C)
    m = best[1]
    return (lambda d: m.predict_proba(T(d))[:, 1]), {"C": best[2], "val_auroc": best[0]}


def fit_all(phase):
    split = "val" if phase == "explore" else "test"
    seeds = [0, 1, 2] if phase == "explore" else [100, 101, 102, 103, 104]
    sfx = "x" if phase == "explore" else "c"
    X = build(); cols = [c for c in X.columns if c not in META]
    (OUT / "preds").mkdir(parents=True, exist_ok=True)
    t0 = time.time(); n = 0
    for f in LEVELS:
        X["cell"] = X.h + "_" + X[f].astype(object).where(X[f].notna(), "UNK").astype(str)
        for model, fit in (("lgbm", fit_lgbm), ("enet_lr", fit_lr)):
            for s in seeds:
                for c in cells_of(f):
                    jid = f"E11_static{sfx}__{f}__{model}__{c}__s{s}__{split}"
                    if (OUT / f"{jid}.json").exists():
                        continue
                    tr = X[(X.cell == c) & (X.split == "train")]; va = X[(X.cell == c) & (X.split == "val")]
                    pr, sel = fit(tr, va, cols, s)
                    res = dict(job_id=jid, factor=f, model=model, train_cell=c, seed=s, split=split, selection=sel, eval={})
                    preds = {}
                    for t in cells_of(f):
                        ev = X[(X.cell == t) & (X.split == split)]
                        p = pr(ev)
                        res["eval"][t] = dict(n=int(len(ev)), events=int(ev.y.sum()), auroc=float(roc_auc_score(ev.y, p)))
                        preds[f"{t}__pid"], preds[f"{t}__y"], preds[f"{t}__p"] = ev.pid.values.astype("U12"), ev.y.values.astype(np.int8), p.astype(np.float32)
                    np.savez_compressed(OUT / "preds" / f"{jid}.npz", **preds)
                    (OUT / f"{jid}.json").write_text(json.dumps(res, indent=1)); n += 1
                    print(jid, {t: round(v["auroc"], 3) for t, v in res["eval"].items()}, flush=True)
    sec = time.time() - t0
    bp = ROOT / "state/budget.json"; b = json.loads(bp.read_text())  # manual ledger entry (in-process run, D27)
    b["per_cycle"]["2"] = b["per_cycle"].get("2", 0) + sec; b["global_seconds"] += sec
    bp.write_text(json.dumps(b, indent=1)); print(f"fitted {n} jobs in {sec:.0f} s (added to budget)")


def analyse(phase, nboot):
    import analyze_transport as AT
    from analyze_v3 import holm, summ, meanD
    split = "val" if phase == "explore" else "test"; sfx = "x" if phase == "explore" else "c"
    rng = np.random.default_rng(20261125)
    R = {"phase": phase, "split": split, "nboot": nboot, "tests": {}, "estimates": {}, "per_cell": {}}
    for f in LEVELS:
        lv = LEVELS[f]; AT.CELLS = cells_of(f)
        AT.src_of = lambda t, lv=lv: (lambda h, l: {"local": t, "unit": f"{h}_{lv[1] if l == lv[0] else lv[0]}",
                                                    "site": f"{'B' if h == 'A' else 'A'}_{l}", "both": f"{'B' if h == 'A' else 'A'}_{lv[1] if l == lv[0] else lv[0]}"})(*t.split("_"))
        for model in ("lgbm", "enet_lr"):
            P = {}
            for fp in (OUT / "preds").glob(f"E11_static{sfx}__{f}__{model}__*__{split}.npz"):
                parts = fp.stem.split("__"); P.setdefault(int(parts[4][1:]), {})[parts[3]] = dict(np.load(fp))
            pt, bs = AT.analyse(P, "hour", nboot, rng); ok = [b for b in bs if len(b) == 4]
            name = f"H7_{f}_{model}"
            R["tests"][name] = summ(meanD(pt), [meanD(b) for b in ok])
            R["estimates"][name] = {k: summ(meanD(pt, k), [meanD(b, k) for b in ok]) for k in ("gap_unit", "gap_site")}
            R["per_cell"][name] = {t: pt[t]["auroc"] for t in AT.CELLS}
    R["holm"] = holm({k: v["p_boot"] for k, v in R["tests"].items()})
    (ROOT / f"results/analysis/v4_{phase}.json").write_text(json.dumps(R, indent=1))
    L = [f"# plan_v4 (static 12-h task) — {phase} ({split}), nboot {nboot}\n", "| test | D [95% CI] | gap_within | gap_site | p (boot) | p (Holm) |", "|---|---|---|---|---|---|"]
    for k, v in R["tests"].items():
        e = R["estimates"][k]
        L.append(f"| {k} | {v['estimate']:.3f} [{v['ci95'][0]:.3f}, {v['ci95'][1]:.3f}] | {e['gap_unit']['estimate']:.3f} | {e['gap_site']['estimate']:.3f} | {v['p_boot']:.4f} | {R['holm'][k]:.4f} |")
    L += ["", "| test | target | local | within-src | site-src | both |", "|---|---|---|---|---|---|"]
    for k, d in R["per_cell"].items():
        for t, a in d.items():
            L.append(f"| {k} | {t} | {a['local']:.3f} | {a['unit']:.3f} | {a['site']:.3f} | {a['both']:.3f} |")
    (ROOT / f"tables/v4_{phase}.md").write_text("\n".join(L) + "\n"); print("\n".join(L))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("cmd", choices=["fit", "analyse"])
    ap.add_argument("--phase", choices=["explore", "confirm"], required=True); ap.add_argument("--nboot", type=int, default=1000)
    a = ap.parse_args()
    if a.cmd == "fit":
        if a.phase == "confirm" and "confirm" not in (ROOT / "experiments/CURRENT_PLAN").read_text() and \
                "confirm" not in (ROOT / "experiments" / (ROOT / "experiments/CURRENT_PLAN").read_text().strip()).read_text().split("phases:")[-1].split("\n")[0]:
            sys.exit("confirm phase not enabled in the current plan (needs plan_v4b)")
        fit_all(a.phase)
    else:
        analyse(a.phase, a.nboot)
