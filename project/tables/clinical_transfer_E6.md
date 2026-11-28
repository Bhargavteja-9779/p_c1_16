# POST HOC: source-transferred thresholds (90% specificity on source held-out stays), E6 test predictions

| model | source | real specificity in target | timely sensitivity (alert ≤ onset) | median lead time, h | alerting stays per 100 |
|---|---|---|---|---|---|
| lgbm | local | 0.900 | 0.544 | 22.7 | 13.2 |
| lgbm | other unit, same hospital | 0.861 | 0.510 | 31.8 | 16.5 |
| lgbm | same unit, other hospital | 0.831 | 0.498 | 32.6 | 19.1 |
| lr | local | 0.900 | 0.480 | 20.1 | 12.7 |
| lr | other unit, same hospital | 0.875 | 0.452 | 42.4 | 14.8 |
| lr | same unit, other hospital | 0.696 | 0.527 | 37.5 | 32.0 |

| model | calibration slope, population transfer | calibration slope, site transfer | difference (95% CI) |
|---|---|---|---|
| lgbm | 0.816 | 0.713 | 0.103 [0.052, 0.190] |
| lr | 0.603 | 0.408 | 0.195 [0.133, 0.295] |
