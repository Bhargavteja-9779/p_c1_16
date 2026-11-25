#!/usr/bin/env python3
"""Figure 1: site excess D (95% CI) for every confirmatory site-excess test, from result files only.
Writes figures/fig1_forest.png and .pdf."""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]
E6 = json.loads((ROOT / "results/analysis/E6_confirm_test.json").read_text())
V3 = json.loads((ROOT / "results/analysis/v3_confirm.json").read_text())
V4 = json.loads((ROOT / "results/analysis/v4_confirm.json").read_text())
rows = [("Hourly task, control: ICU unit", None)]
for k, lab in (("lgbm_hour", "Gradient boosting"), ("lr_hour", "Logistic regression")):
    rows.append((lab, (E6["H1"][k]["D"], E6["holm"][f"H1_{k}"]["p_holm"])))
for f, title in (("age", "age band"), ("route", "admission route")):
    rows.append((f"Hourly task, control: {title}", None))
    for m, lab in (("lgbm", "Gradient boosting"), ("lr", "Logistic regression")):
        rows.append((lab, (V3["tests"][f"H4_{f}_{m}"], V3["holm"][f"H4_{f}_{m}"])))
rows.append(("Hourly task, size-matched training (unit)", None))
for m, lab in (("lgbm", "Gradient boosting"), ("lr", "Logistic regression")):
    rows.append((lab, (V3["tests"][f"H6_matched_{m}"], V3["holm"][f"H6_matched_{m}"])))
for f, title in (("unit", "ICU unit"), ("route", "admission route")):
    rows.append((f"Static 12-h task, control: {title}", None))
    for m, lab in (("lgbm", "Gradient boosting"), ("enet_lr", "Logistic regression")):
        rows.append((lab, (V4["tests"][f"H7_{f}_{m}"], V4["holm"][f"H7_{f}_{m}"])))
fig, ax = plt.subplots(figsize=(7.4, 0.33 * len(rows) + 0.8))
y = len(rows)
for lab, v in rows:
    y -= 1
    if v is None:
        ax.text(-0.13, y, lab, fontsize=8.5, fontweight="bold", va="center"); continue
    d, ph = v
    col = "#1f4e79" if ph < 0.05 else "#9aa5b1"
    ax.errorbar(d["estimate"], y, xerr=[[d["estimate"] - d["ci95"][0]], [d["ci95"][1] - d["estimate"]]], fmt="o",
                color=col, ms=4.5, capsize=2, lw=1.3)
    ax.text(-0.125, y, lab, fontsize=8, va="center")
    ax.text(0.13, y, f"{d['estimate']:.3f} [{d['ci95'][0]:.3f}, {d['ci95'][1]:.3f}]   Holm p {ph:.3f}", fontsize=7.5, va="center")
ax.axvline(0, color="k", lw=0.8)
ax.set_xlim(-0.13, 0.125); ax.set_ylim(-0.7, len(rows) - 0.3); ax.set_yticks([])
ax.set_xticks([-0.04, 0, 0.04, 0.08, 0.12])
ax.set_xlabel("Site excess D = cross-hospital gap minus within-hospital gap (AUROC)", fontsize=8.5)
for s in ("left", "right", "top"):
    ax.spines[s].set_visible(False)
ax.tick_params(labelsize=8)
fig.text(0.01, -0.01, "Test sets, seeds 100-104; patient-cluster bootstrap 95% CI. Dark: Holm p < 0.05 within its pre-registered family; grey: not significant.", fontsize=6.8)
(ROOT / "figures").mkdir(exist_ok=True)
fig.savefig(ROOT / "figures/fig1_forest.png", dpi=200, bbox_inches="tight")
fig.savefig(ROOT / "figures/fig1_forest.pdf", bbox_inches="tight")
print("ok")
