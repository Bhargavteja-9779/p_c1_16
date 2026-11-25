# E6 secondary outcomes (test; mean of 4 target cells x 5 seeds; seed SD in parentheses)

| model | role | AUROC | AUPRC | calibration slope | calibration-in-the-large |
|---|---|---|---|---|---|
| lgbm | local | 0.834 (0.002) | 0.099 (0.003) | 0.840 (0.031) | -0.119 (0.042) |
| lgbm | unit | 0.789 (0.003) | 0.082 (0.005) | 0.816 (0.015) | -0.283 (0.041) |
| lgbm | site | 0.763 (0.001) | 0.064 (0.002) | 0.713 (0.035) | -0.244 (0.064) |
| lgbm | both | 0.735 (0.006) | 0.063 (0.004) | 0.726 (0.019) | -0.380 (0.060) |
| lr | local | 0.789 (0.000) | 0.085 (0.000) | 0.691 (0.000) | -0.245 (0.000) |
| lr | unit | 0.737 (0.000) | 0.071 (0.000) | 0.603 (0.000) | -0.234 (0.000) |
| lr | site | 0.674 (0.000) | 0.054 (0.000) | 0.408 (0.000) | -0.912 (0.000) |
| lr | both | 0.667 (0.000) | 0.060 (0.000) | 0.345 (0.000) | -1.366 (0.000) |

# POST HOC: pre-onset hour-level AUROC (post-onset positive hours removed)

| model | local | population source | site source | gap population | gap site | D |
|---|---|---|---|---|---|---|
| lgbm | 0.826 | 0.774 | 0.755 | 0.052 [0.033, 0.071] | 0.071 [0.051, 0.090] | 0.019 [-0.006, 0.041] |
| lr | 0.779 | 0.726 | 0.666 | 0.053 [0.029, 0.077] | 0.112 [0.085, 0.142] | 0.059 [0.027, 0.094] |
