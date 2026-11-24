# E6_confirm (test) — transport gaps (AUROC; gap = local − transported; mean of 4 target cells)

| model/level | gap_unit [95% CI] | gap_site [95% CI] | D = site − unit [95% CI] | p (boot) | site/unit ratio |
|---|---|---|---|---|---|
| lgbm_hour | 0.045 [0.027, 0.061] | 0.071 [0.053, 0.090] | 0.026 [0.005, 0.049] | 0.0180 | 1.59 |
| lgbm_patient | 0.048 [0.025, 0.072] | 0.087 [0.062, 0.110] | 0.039 [0.010, 0.067] | 0.0150 | 1.82 |
| lr_hour | 0.052 [0.027, 0.077] | 0.116 [0.087, 0.146] | 0.063 [0.031, 0.098] | 0.0005 | 2.21 |
| lr_patient | 0.053 [0.025, 0.079] | 0.101 [0.069, 0.132] | 0.048 [0.014, 0.081] | 0.0025 | 1.89 |

## Unlabelled site fixes (LightGBM, hour level)

| fixes | D (site − unit) | share of site component removed [95% CI] | P(share ≥ 0.5) | gap_site | gap_unit |
|---|---|---|---|---|---|
| none | 0.026 | — | — | — | — |
| harm | 0.028 | -0.07 [-0.62, 0.26] | 0.008 | 0.073 | 0.045 |
| harm_noproc | 0.014 | 0.48 [-0.05, 2.06] | 0.457 | 0.063 | 0.050 |
| harm_noproc_norm | 0.004 | 0.85 [0.26, 3.13] | 0.868 | 0.051 | 0.047 |

## Per target cell (hour-level AUROC by source role)

| model | target | local | unit-src | site-src | both | D |
|---|---|---|---|---|---|---|
| lgbm_hour | A_MICU | 0.806 | 0.726 | 0.699 | 0.699 | 0.026 |
| lgbm_hour | A_SICU | 0.836 | 0.809 | 0.781 | 0.725 | 0.028 |
| lgbm_hour | B_MICU | 0.841 | 0.814 | 0.778 | 0.742 | 0.036 |
| lgbm_hour | B_SICU | 0.853 | 0.809 | 0.793 | 0.774 | 0.016 |
| lr_hour | A_MICU | 0.759 | 0.725 | 0.627 | 0.696 | 0.097 |
| lr_hour | A_SICU | 0.804 | 0.738 | 0.694 | 0.581 | 0.044 |
| lr_hour | B_MICU | 0.786 | 0.734 | 0.648 | 0.718 | 0.085 |
| lr_hour | B_SICU | 0.808 | 0.751 | 0.725 | 0.673 | 0.026 |
| lgbm_hour_harm | A_MICU | 0.806 | 0.732 | 0.699 | 0.703 | 0.033 |
| lgbm_hour_harm | A_SICU | 0.845 | 0.812 | 0.782 | 0.708 | 0.030 |
| lgbm_hour_harm | B_MICU | 0.840 | 0.813 | 0.783 | 0.742 | 0.029 |
| lgbm_hour_harm | B_SICU | 0.852 | 0.808 | 0.787 | 0.782 | 0.021 |
| lgbm_hour_harm_noproc | A_MICU | 0.798 | 0.711 | 0.695 | 0.689 | 0.016 |
| lgbm_hour_harm_noproc | A_SICU | 0.801 | 0.764 | 0.773 | 0.703 | -0.009 |
| lgbm_hour_harm_noproc | B_MICU | 0.829 | 0.782 | 0.778 | 0.728 | 0.003 |
| lgbm_hour_harm_noproc | B_SICU | 0.830 | 0.804 | 0.759 | 0.759 | 0.045 |
| lgbm_hour_harm_noproc_norm | A_MICU | 0.798 | 0.720 | 0.730 | 0.688 | -0.009 |
| lgbm_hour_harm_noproc_norm | A_SICU | 0.790 | 0.761 | 0.779 | 0.707 | -0.018 |
| lgbm_hour_harm_noproc_norm | B_MICU | 0.831 | 0.779 | 0.767 | 0.734 | 0.012 |
| lgbm_hour_harm_noproc_norm | B_SICU | 0.833 | 0.802 | 0.771 | 0.731 | 0.031 |

## Holm-corrected family

| test | p (boot) | p (Holm) |
|---|---|---|
| H1_lgbm_hour | 0.0180 | 0.0180 |
| H1_lr_hour | 0.0005 | 0.0015 |
| H2_reduction | 0.0050 | 0.0100 |
