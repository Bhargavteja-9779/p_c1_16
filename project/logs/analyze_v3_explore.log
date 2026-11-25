# plan_v3 analysis — explore (val), nboot 1000

## Confirmatory family (Holm)

| test | estimate [95% CI] | p (boot) | p (Holm) |
|---|---|---|---|
| H4_age_lgbm | 0.063 [0.050, 0.077] | 0.0010 | 0.0070 |
| H4_age_lr | 0.100 [0.077, 0.122] | 0.0010 | 0.0070 |
| H4_route_lgbm | 0.036 [0.019, 0.052] | 0.0010 | 0.0070 |
| H4_route_lr | 0.076 [0.054, 0.102] | 0.0010 | 0.0070 |
| H5_Dall_minus_Dvitals | 0.023 [0.002, 0.045] | 0.0320 | 0.0320 |
| H6_matched_lgbm | 0.043 [0.021, 0.064] | 0.0010 | 0.0070 |
| H6_matched_lr | 0.055 [0.022, 0.091] | 0.0010 | 0.0070 |

## Estimates

| quantity | estimate [95% CI] |
|---|---|
| H4_age_lgbm.gap_unit | 0.004 [-0.005, 0.012] |
| H4_age_lgbm.gap_site | 0.067 [0.054, 0.080] |
| H4_age_lgbm_patient | 0.071 [0.053, 0.093] |
| H4_age_lr.gap_unit | 0.009 [-0.004, 0.024] |
| H4_age_lr.gap_site | 0.108 [0.087, 0.129] |
| H4_age_lr_patient | 0.108 [0.086, 0.133] |
| H4_route_lgbm.gap_unit | 0.033 [0.022, 0.045] |
| H4_route_lgbm.gap_site | 0.069 [0.055, 0.084] |
| H4_route_lgbm_patient | 0.040 [0.021, 0.056] |
| H4_route_lr.gap_unit | 0.034 [0.016, 0.052] |
| H4_route_lr.gap_site | 0.110 [0.089, 0.135] |
| H4_route_lr_patient | 0.082 [0.053, 0.111] |
| H5_D_all | 0.043 [0.021, 0.066] |
| H5_gapsite_all | 0.078 [0.058, 0.099] |
| H5_gapunit_all | 0.035 [0.018, 0.052] |
| H5_D_vitals | 0.020 [-0.008, 0.048] |
| H5_gapsite_vitals | 0.057 [0.032, 0.083] |
| H5_gapunit_vitals | 0.038 [0.014, 0.060] |
| H5_D_labs | 0.019 [-0.011, 0.049] |
| H5_gapsite_labs | 0.068 [0.043, 0.090] |
| H5_gapunit_labs | 0.049 [0.027, 0.072] |
| H5_D_noproc | 0.020 [-0.002, 0.042] |
| H5_gapsite_noproc | 0.059 [0.037, 0.079] |
| H5_gapunit_noproc | 0.039 [0.017, 0.060] |
| H5_D_proc | 0.056 [0.031, 0.079] |
| H5_gapsite_proc | 0.098 [0.074, 0.122] |
| H5_gapunit_proc | 0.042 [0.024, 0.063] |
| E10_pooled_minus_unitsrc | 0.010 [-0.002, 0.023] |
| E10_pooled_minus_sitesrc | 0.053 [0.039, 0.068] |

## Domain-classifier AUC (shift size)

| factor | pair | AUC |
|---|---|---|
| unit | A_MICU vs A_SICU | 0.968 |
| unit | B_MICU vs B_SICU | 0.902 |
| unit | A_MICU vs B_MICU | 1.000 |
| unit | A_SICU vs B_SICU | 1.000 |
| age | A_Y vs A_O | 0.816 |
| age | B_Y vs B_O | 0.781 |
| age | A_Y vs B_Y | 1.000 |
| age | A_O vs B_O | 1.000 |
| route | A_D vs A_L | 0.714 |
| route | B_D vs B_L | 0.779 |
| route | A_D vs B_D | 1.000 |
| route | A_L vs B_L | 1.000 |
