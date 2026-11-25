# 2026-11-24 — RESULT (exploration, VALIDATION, seeds 0–2): factorial transport, fixes, estimators

Files: `tables/E1_explore_val_transport.md`, `results/analysis/E1_explore_val.json`, `tables/E5_E1_explore_val.md`.
60 fits (E1: 24, E2: 36), all completed, none failed.

**H1 direction holds in every cell.** Hour-level AUROC gaps (local − transported), mean of 4 target cells:
- LightGBM: unit gap 0.035 [0.017, 0.052]; site gap 0.078 [0.058, 0.101]; D = 0.043 [0.021, 0.066]; ratio 2.2.
- Logistic regression: unit gap 0.054; site gap 0.119; D = 0.066 [0.030, 0.102]; ratio 2.2.
- D > 0 in all 4 target cells for both model classes. Patient-level results agree (ratio ≈ 2.0).

**H2 as I wrote it is contradicted (SURPRISE).** I expected unlabelled fixes to remove less than half of the site component. On validation, fixes in combination remove about 0.61 of it [0.33, 1.29]:
- harmonisation alone: 0.20
- plus dropping process features: 0.47
- plus per-site normalisation: 0.61

The site gap falls from 0.078 to 0.053 while the unit gap stays at about 0.035. I had concluded from hospital-level training (entry 007) that fixes recover ≤ 0.013. That was too pessimistic once the comparison is matched by unit. I am not hiding this. H2 becomes an estimation target for confirmation (plan_v2, D17), and the story changes to: "about half of the site penalty can be removed without labels; the rest cannot".

**H3 holds.** Label-free estimates of transported AUROC are off by more than 0.03 in 64–92% of transfer×seed cases:
- The developer's internal AUROC is optimistic: mean error +0.071 for LightGBM, +0.097 for LR.
- The model-implied AUROC is also optimistic.
- Importance weighting is unbiased on average but noisy. The MAE is 0.076, because cross-site domain AUC is about 0.9999. Even units within one hospital are separable (0.90–0.97).

**Few-label checks are expensive.** With a split-half reference, labelling 400 local patients gives an AUROC within ±0.03 only 43% of the time (LightGBM), or 35% (LR). My first version said 90% at n = 800. That number was finite-population optimism, so I replaced the design before any confirmation run.
