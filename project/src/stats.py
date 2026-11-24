"""Statistics utilities: metrics, bootstrap CIs, paired tests, effect sizes, Holm correction."""
import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score, average_precision_score


def auroc(y, p):
    return float(roc_auc_score(y, p))


def auprc(y, p):
    return float(average_precision_score(y, p))


def brier(y, p):
    return float(np.mean((np.asarray(p) - np.asarray(y)) ** 2))


def calibration_slope_intercept(y, p, eps=1e-6):
    """Logistic recalibration: logit(P(y=1)) = a + b*logit(p). Returns (intercept a, slope b),
    plus calibration-in-the-large (mean(y) - mean(p))."""
    import statsmodels.api as sm
    p = np.clip(np.asarray(p, float), eps, 1 - eps)
    lp = np.log(p / (1 - p))
    try:
        fit = sm.GLM(np.asarray(y), sm.add_constant(lp), family=sm.families.Binomial()).fit()
        a, b = fit.params
    except Exception:
        a, b = np.nan, np.nan
    # calibration-in-the-large: intercept with slope fixed at 1 (offset)
    try:
        fit0 = sm.GLM(np.asarray(y), np.ones_like(lp), family=sm.families.Binomial(), offset=lp).fit()
        citl = float(fit0.params[0])
    except Exception:
        citl = np.nan
    return float(a), float(b), citl


def ece(y, p, bins=10):
    y, p = np.asarray(y), np.asarray(p)
    q = np.quantile(p, np.linspace(0, 1, bins + 1))
    idx = np.clip(np.searchsorted(q, p, side="right") - 1, 0, bins - 1)
    e = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            e += m.mean() * abs(y[m].mean() - p[m].mean())
    return float(e)


def bootstrap_ci(values, n_boot=10000, alpha=0.05, seed=0):
    """Percentile bootstrap CI of the mean of `values` (e.g. per-seed paired differences)."""
    v = np.asarray(values, float)
    rng = np.random.default_rng(seed)
    means = rng.choice(v, size=(n_boot, len(v)), replace=True).mean(1)
    return float(np.quantile(means, alpha / 2)), float(np.quantile(means, 1 - alpha / 2))


def paired_bootstrap_metric(y, p_a, p_b, metric=auroc, n_boot=2000, seed=0, groups=None):
    """Bootstrap over patients (or groups) of metric(p_a) - metric(p_b) on the same test set.
    Returns (diff, ci_low, ci_high, two-sided p-value via bootstrap sign test)."""
    y, p_a, p_b = map(np.asarray, (y, p_a, p_b))
    rng = np.random.default_rng(seed)
    d0 = metric(y, p_a) - metric(y, p_b)
    if groups is None:
        n = len(y)
        idx_fn = lambda: rng.integers(0, n, n)
    else:
        g = np.asarray(groups)
        ug, inv = np.unique(g, return_inverse=True)
        members = [np.where(inv == i)[0] for i in range(len(ug))]
        idx_fn = lambda: np.concatenate([members[i] for i in rng.integers(0, len(ug), len(ug))])
    ds = []
    for _ in range(n_boot):
        ii = idx_fn()
        if y[ii].min() == y[ii].max():
            continue
        ds.append(metric(y[ii], p_a[ii]) - metric(y[ii], p_b[ii]))
    ds = np.asarray(ds)
    lo, hi = np.quantile(ds, [0.025, 0.975])
    p = 2 * min((ds <= 0).mean(), (ds >= 0).mean())
    return float(d0), float(lo), float(hi), float(min(1.0, max(p, 1.0 / len(ds))))


def paired_tests(a, b):
    """Paired comparison of per-seed metrics a (method) vs b (baseline)."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = a - b
    out = {"mean_diff": float(d.mean()), "sd_diff": float(d.std(ddof=1)) if len(d) > 1 else float("nan"), "n": int(len(d))}
    out["t_p"] = float(stats.ttest_rel(a, b).pvalue) if len(d) > 1 else float("nan")
    try:
        out["wilcoxon_p"] = float(stats.wilcoxon(a, b).pvalue)
    except ValueError:
        out["wilcoxon_p"] = float("nan")
    out["cohen_dz"] = float(d.mean() / d.std(ddof=1)) if len(d) > 1 and d.std(ddof=1) > 0 else float("nan")
    out["ci95"] = bootstrap_ci(d) if len(d) > 1 else (float("nan"), float("nan"))
    return out


def holm(pvals):
    """Holm–Bonferroni adjusted p-values (same order as input)."""
    p = np.asarray(pvals, float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    run = 0.0
    for k, i in enumerate(order):
        run = max(run, (m - k) * p[i])
        adj[i] = min(1.0, run)
    return adj.tolist()


def mean_ci(x):
    x = np.asarray(x, float)
    if len(x) < 2:
        return float(x.mean()), float("nan"), float("nan"), float("nan")
    m, s = x.mean(), x.std(ddof=1)
    h = stats.t.ppf(0.975, len(x) - 1) * s / np.sqrt(len(x))
    return float(m), float(s), float(m - h), float(m + h)
