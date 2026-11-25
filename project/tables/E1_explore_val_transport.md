# E1_explore (val) — transport gaps (AUROC; gap = local − transported; mean of 4 target cells)

| model/level | gap_unit [95% CI] | gap_site [95% CI] | D = site − unit [95% CI] | p (boot) | site/unit ratio |
|---|---|---|---|---|---|
| lgbm_hour | 0.035 [0.017, 0.052] | 0.078 [0.058, 0.101] | 0.043 [0.021, 0.066] | 0.0020 | 2.22 |
| lgbm_patient | 0.046 [0.024, 0.066] | 0.090 [0.064, 0.116] | 0.044 [0.012, 0.071] | 0.0100 | 1.97 |
| lr_hour | 0.054 [0.029, 0.080] | 0.119 [0.090, 0.152] | 0.066 [0.030, 0.102] | 0.0010 | 2.22 |
| lr_patient | 0.061 [0.028, 0.092] | 0.128 [0.097, 0.156] | 0.068 [0.036, 0.100] | 0.0050 | 2.12 |

## Unlabelled site fixes (LightGBM, hour level)

| fixes | D (site − unit) | share of site component removed [95% CI] | P(share ≥ 0.5) | gap_site | gap_unit |
|---|---|---|---|---|---|
| none | 0.043 | — | — | — | — |
| harm | 0.035 | 0.20 [-0.02, 0.46] | 0.016 | 0.066 | 0.031 |
| harm_noproc | 0.023 | 0.47 [0.17, 1.08] | 0.436 | 0.058 | 0.035 |
| harm_noproc_norm | 0.017 | 0.61 [0.33, 1.29] | 0.725 | 0.053 | 0.036 |

## Per target cell (hour-level AUROC by source role)

| model | target | local | unit-src | site-src | both | D |
|---|---|---|---|---|---|---|
| lgbm_hour | A_MICU | 0.775 | 0.750 | 0.719 | 0.693 | 0.031 |
| lgbm_hour | A_SICU | 0.804 | 0.784 | 0.745 | 0.727 | 0.039 |
| lgbm_hour | B_MICU | 0.865 | 0.808 | 0.776 | 0.711 | 0.032 |
| lgbm_hour | B_SICU | 0.861 | 0.823 | 0.752 | 0.781 | 0.071 |
| lr_hour | A_MICU | 0.723 | 0.700 | 0.660 | 0.700 | 0.040 |
| lr_hour | A_SICU | 0.781 | 0.751 | 0.660 | 0.598 | 0.090 |
| lr_hour | B_MICU | 0.833 | 0.743 | 0.647 | 0.686 | 0.096 |
| lr_hour | B_SICU | 0.820 | 0.748 | 0.711 | 0.700 | 0.037 |
| lgbm_hour_harm | A_MICU | 0.778 | 0.756 | 0.731 | 0.696 | 0.025 |
| lgbm_hour_harm | A_SICU | 0.803 | 0.785 | 0.754 | 0.746 | 0.031 |
| lgbm_hour_harm | B_MICU | 0.861 | 0.803 | 0.785 | 0.714 | 0.018 |
| lgbm_hour_harm | B_SICU | 0.860 | 0.831 | 0.768 | 0.785 | 0.064 |
| lgbm_hour_harm_noproc | A_MICU | 0.764 | 0.726 | 0.711 | 0.675 | 0.016 |
| lgbm_hour_harm_noproc | A_SICU | 0.761 | 0.755 | 0.738 | 0.733 | 0.016 |
| lgbm_hour_harm_noproc | B_MICU | 0.846 | 0.784 | 0.797 | 0.719 | -0.013 |
| lgbm_hour_harm_noproc | B_SICU | 0.852 | 0.817 | 0.745 | 0.773 | 0.072 |
| lgbm_hour_harm_noproc_norm | A_MICU | 0.765 | 0.732 | 0.737 | 0.696 | -0.005 |
| lgbm_hour_harm_noproc_norm | A_SICU | 0.762 | 0.751 | 0.743 | 0.744 | 0.008 |
| lgbm_hour_harm_noproc_norm | B_MICU | 0.845 | 0.782 | 0.792 | 0.724 | -0.009 |
| lgbm_hour_harm_noproc_norm | B_SICU | 0.851 | 0.814 | 0.740 | 0.762 | 0.074 |

## Holm-corrected family

| test | p (boot) | p (Holm) |
|---|---|---|
| H1_lgbm_hour | 0.0020 | 0.0030 |
| H1_lr_hour | 0.0010 | 0.0030 |
| H2_reduction | 0.0010 | 0.0030 |
