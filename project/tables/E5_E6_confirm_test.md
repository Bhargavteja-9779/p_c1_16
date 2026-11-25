# E5 (E6_confirm, test) — estimating transported AUROC (hour level)

| model | estimator | MAE | mean error | share |err| > 0.03 | n transfers×seeds |
|---|---|---|---|---|---|
| lgbm | internal | 0.072 | +0.072 | 0.80 | 60 |
| lgbm | implied | 0.064 | +0.045 | 0.77 | 60 |
| lgbm | iw | 0.067 | +0.003 | 0.77 | 60 |
| lr | internal | 0.097 | +0.097 | 0.92 | 60 |
| lr | implied | 0.164 | +0.164 | 1.00 | 60 |
| lr | iw | 0.138 | -0.086 | 0.92 | 60 |

## Few-label local check (split-half): P(|AUROC on n local patients − AUROC on disjoint half| ≤ 0.03), mean over 12 transfers

| model | n=50 | n=100 | n=200 | n=400 |
|---|---|---|---|---|
| lgbm | 0.16 | 0.23 | 0.32 | 0.41 |
| lr | 0.14 | 0.20 | 0.29 | 0.37 |
