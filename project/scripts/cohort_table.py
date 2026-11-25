#!/usr/bin/env python3
"""Table: patient characteristics per cell (hospital x unit) and for stays without a recorded unit (excluded from
unit analyses). Writes results/cohort_table.json and tables/cohort_table.md. Idempotent."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
raw = pd.read_parquet(ROOT / "data/processed/physionet2019.parquet")
g = raw.groupby("pid")
u = raw.assign(unit=np.where(raw.Unit1 == 1, "MICU", np.where(raw.Unit2 == 1, "SICU", None))).dropna(subset=["unit"]).groupby("pid").unit.first()
labs = ["Lactate", "WBC", "Creatinine", "Platelets"]
P = pd.DataFrame({"hospital": g.hospital.first(), "age": g.Age.first(), "female": (g.Gender.first() == 0).astype(int),
                  "hadm": g.HospAdmTime.first(), "los": g.size(), "sep": g.SepsisLabel.max()})
P["unit"] = u.reindex(P.index).fillna("none")
onset = raw[raw.SepsisLabel == 1].groupby("pid").ICULOS.min() + 6  # label starts 6 h before onset
P["onset_h"] = onset.reindex(P.index)
for l in labs:
    P[f"{l}_ever"] = g[l].apply(lambda s: s.notna().any()).astype(int)
P["direct"] = (P.hadm >= -24).astype(float).where(P.hadm.notna())
P["cell"] = P.hospital + "_" + P.unit
rows = {}
for c, d in P.groupby("cell"):
    rows[c] = {"stays": int(len(d)), "sepsis_pct": round(float(100 * d.sep.mean()), 1), "age_median": float(d.age.median()),
               "age_iqr": [float(d.age.quantile(.25)), float(d.age.quantile(.75))], "female_pct": round(float(100 * d.female.mean()), 1),
               "icu_within_24h_pct": round(float(100 * d.direct.mean()), 1), "los_h_median": float(d.los.median()),
               "onset_h_median": float(d.onset_h.median()) if d.sep.sum() else None,
               **{f"{l}_measured_pct": round(float(100 * d[f"{l}_ever"].mean()), 1) for l in labs}}
(ROOT / "results/cohort_table.json").write_text(json.dumps(rows, indent=1))
order = ["A_MICU", "A_SICU", "A_none", "B_MICU", "B_SICU", "B_none"]
L = ["| Characteristic | " + " | ".join(order) + " |", "|---" * (len(order) + 1) + "|"]
def row(name, f): L.append(f"| {name} | " + " | ".join(f(rows[c]) for c in order) + " |")
row("Stays, n", lambda r: f"{r['stays']:,}")
row("Sepsis, %", lambda r: f"{r['sepsis_pct']}")
row("Age, median (IQR), y", lambda r: f"{r['age_median']:.0f} ({r['age_iqr'][0]:.0f}–{r['age_iqr'][1]:.0f})")
row("Female, %", lambda r: f"{r['female_pct']}")
row("ICU admission within 24 h of hospital admission, %", lambda r: f"{r['icu_within_24h_pct']}")
row("ICU records, median hours", lambda r: f"{r['los_h_median']:.0f}")
row("Sepsis onset, median ICU hour", lambda r: "—" if r["onset_h_median"] is None else f"{r['onset_h_median']:.0f}")
for l in labs:
    row(f"{l} ever measured, %", lambda r, l=l: f"{r[l + '_measured_pct']}")
(ROOT / "tables/cohort_table.md").write_text("\n".join(L) + "\n"); print("\n".join(L))
