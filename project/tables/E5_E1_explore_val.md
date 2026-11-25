# E5 (E1_explore, val) — estimating transported AUROC (hour level)

| model | estimator | MAE | mean error | share |err| > 0.03 | n transfers×seeds |
|---|---|---|---|---|---|
| lgbm | internal | 0.074 | +0.071 | 0.75 | 36 |
| lgbm | implied | 0.065 | +0.043 | 0.64 | 36 |
| lgbm | iw | 0.076 | -0.006 | 0.81 | 36 |
| lr | internal | 0.102 | +0.097 | 0.83 | 36 |
| lr | implied | 0.144 | +0.144 | 0.92 | 36 |
| lr | iw | 0.053 | -0.013 | 0.75 | 36 |

## Few-label local check (split-half): P(|AUROC on n local patients − AUROC on disjoint half| ≤ 0.03), mean over 12 transfers

| model | n=50 | n=100 | n=200 | n=400 |
|---|---|---|---|---|
| lgbm | 0.19 | 0.26 | 0.35 | 0.43 |
| lr | 0.14 | 0.21 | 0.29 | 0.35 |
