# plan_v3 analysis — confirm (test), nboot 2000

## Confirmatory family (Holm)

| test | estimate [95% CI] | p (boot) | p (Holm) |
|---|---|---|---|
| H4_age_lgbm | 0.058 [0.045, 0.072] | 0.0005 | 0.0035 |
| H4_age_lr | 0.091 [0.069, 0.113] | 0.0005 | 0.0035 |
| H4_route_lgbm | 0.023 [0.008, 0.038] | 0.0020 | 0.0060 |
| H4_route_lr | 0.081 [0.056, 0.107] | 0.0005 | 0.0035 |
| H5_Dall_minus_Dvitals | 0.018 [-0.001, 0.036] | 0.0590 | 0.0640 |
| H6_matched_lgbm | 0.023 [0.002, 0.045] | 0.0320 | 0.0640 |
| H6_matched_lr | 0.062 [0.030, 0.095] | 0.0005 | 0.0035 |

## Estimates

| quantity | estimate [95% CI] |
|---|---|
| H4_age_lgbm.gap_unit | 0.004 [-0.005, 0.013] |
| H4_age_lgbm.gap_site | 0.062 [0.050, 0.075] |
| H4_age_lgbm_patient | 0.076 [0.056, 0.096] |
| H4_age_lr.gap_unit | 0.003 [-0.009, 0.014] |
| H4_age_lr.gap_site | 0.094 [0.072, 0.116] |
| H4_age_lr_patient | 0.094 [0.072, 0.115] |
| H4_route_lgbm.gap_unit | 0.026 [0.014, 0.039] |
| H4_route_lgbm.gap_site | 0.050 [0.036, 0.064] |
| H4_route_lgbm_patient | 0.027 [0.011, 0.045] |
| H4_route_lr.gap_unit | 0.035 [0.021, 0.049] |
| H4_route_lr.gap_site | 0.115 [0.091, 0.141] |
| H4_route_lr_patient | 0.066 [0.043, 0.090] |
| H5_D_all | 0.026 [0.005, 0.049] |
| H5_gapsite_all | 0.071 [0.054, 0.089] |
| H5_gapunit_all | 0.045 [0.027, 0.062] |
| H5_D_vitals | 0.009 [-0.016, 0.034] |
| H5_gapsite_vitals | 0.067 [0.045, 0.089] |
| H5_gapunit_vitals | 0.058 [0.035, 0.081] |
| H5_D_labs | 0.008 [-0.016, 0.033] |
| H5_gapsite_labs | 0.050 [0.031, 0.070] |
| H5_gapunit_labs | 0.042 [0.020, 0.063] |
| H5_D_noproc | 0.009 [-0.015, 0.033] |
| H5_gapsite_noproc | 0.056 [0.037, 0.076] |
| H5_gapunit_noproc | 0.047 [0.025, 0.068] |
| H5_D_proc | 0.046 [0.022, 0.070] |
| H5_gapsite_proc | 0.092 [0.072, 0.113] |
| H5_gapunit_proc | 0.046 [0.029, 0.063] |
| E10_pooled_minus_unitsrc | 0.012 [-0.000, 0.026] |
| E10_pooled_minus_sitesrc | 0.038 [0.024, 0.054] |

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
