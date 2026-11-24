# 2026-11-24 — DIAGNOSIS: where the A↔B drop comes from (validation only, seed 0)

Files: `results/diagnosis/diag_*.json`, `subgroups_s0.csv`, `shift_s0.json`, `proto_sitenorm_s0.json`.

What I saw (hour-level AUROC, internal S-val → external T-val, LightGBM, all feature groups):
- A→B 0.814 → 0.779; B→A 0.865 → 0.759. Seeds 0–2 move these by ≤ 0.009.
- Removing measurement-process features did not close the gap. For A→B, external AUROC was a little better without them (0.789 vs 0.779), even though internal was worse (0.787 vs 0.814), so internal validation ranked these two variants the wrong way round for external use. For B→A it changed almost nothing (0.753 vs 0.759).
- **Even a vitals-only model drops B→A, 0.758 → 0.625.** Measurement patterns cannot be the whole story.
- Splitting positives by type does not explain it either. Incident-sepsis patients drop as much as prevalent ones (B→A incident 0.858 → 0.770). Prevalent means septic from the first recorded hour: 11.3% of septic patients in A, 19.5% in B.
- Pooled A+B training reaches the local level on both sites (A 0.817, B 0.859). The shift is learnable once both sites are in the training data.
- A domain classifier separates the hospitals almost perfectly (AUC 0.99995), even without process features. Importance weighting is therefore degenerate (ESS 2–5%) and gives wrong external estimates (A→B estimated 0.731 vs observed 0.779; B→A 0.799 vs 0.759).
- Per-site quantile normalisation of features, fitted on unlabelled train rows, helps only a little (B→A 0.759 → 0.772 at best).

SURPRISE, from the reason the sites are separable: there are encoding and harmonisation differences in the raw data.
- Age is stored with decimals in A (5971 unique values) and as integers in B (77 unique).
- EtCO2 is never recorded in A.
- 19% of B's Calcium values are < 2. That looks like ionised calcium in mmol/L mixed with total calcium in mg/dL; A has none.
- TroponinI and Bilirubin_direct have very different distributions (TroponinI median 4.3 in A vs 0.22 in B), which suggests different assays or units.

Next: check whether these artefacts are already documented, and whether they matter for transport.
