# 2026-11-24 — DIAGNOSIS: unit shift vs site shift (validation, seed 0)

Two things I checked today, in order.

1. **Can I decompose the cross-hospital shift with density ratios?** No. After repairing the encoding artefacts, a domain classifier still separates A from B almost perfectly (AUC 0.9996 with all features; 0.978 with vital-sign values and trends only). The vitals-only separation is driven by Temp and DBP. Their resolution differs between sites (A has 597 distinct Temp values vs 209 in B), so even "physiology" carries a charting fingerprint. Any covariate/concept decomposition based on overlap would be dominated by the non-overlap region (`results/diagnosis/proto_overlap.json`).

2. **A control that needs no density ratios: transfer between ICU units inside a hospital, where encoding is identical** (`results/diagnosis/unitshift_s0.json`). Below, gap = the target's own local model minus the transported model, hour-level AUROC on validation.
   - Within hospital, other unit: A MICU→SICU 0.058; A SICU→MICU 0.002; B MICU→SICU 0.059; B SICU→MICU 0.035. Mean ≈ 0.039.
   - Other hospital, same unit: B→A MICU 0.068; B→A SICU 0.063; A→B MICU 0.079; A→B SICU 0.127. Mean ≈ 0.084.

So moving between units in the same hospital already costs something (case mix and clinical context). Moving between hospitals costs roughly twice as much. This factorial (unit × hospital) is a cleaner way to estimate a "site component" than density ratios. These are single-seed validation numbers on cells of about 1,000 patients, so they need CIs and the confirmation seeds before they mean anything.

Prior-art note: few-label performance estimation is well covered (prediction-powered inference 2023, active testing 2021, active surrogate estimators 2022, SSME NeurIPS 2025). I am dropping a "new estimator" claim (old H3) and will use existing estimators only as tools.
