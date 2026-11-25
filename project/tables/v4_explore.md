# plan_v4 (static 12-h task) — explore (val), nboot 1000

| test | D [95% CI] | gap_within | gap_site | p (boot) | p (Holm) |
|---|---|---|---|---|---|
| H7_unit_lgbm | -0.018 [-0.061, 0.027] | 0.103 | 0.085 | 0.4620 | 1.0000 |
| H7_unit_enet_lr | 0.004 [-0.049, 0.057] | 0.101 | 0.105 | 0.8920 | 1.0000 |
| H7_route_lgbm | 0.046 [0.013, 0.078] | 0.055 | 0.101 | 0.0060 | 0.0240 |
| H7_route_enet_lr | 0.016 [-0.026, 0.057] | 0.066 | 0.082 | 0.4900 | 1.0000 |

| test | target | local | within-src | site-src | both |
|---|---|---|---|---|---|
| H7_unit_lgbm | A_MICU | 0.703 | 0.646 | 0.667 | 0.625 |
| H7_unit_lgbm | A_SICU | 0.716 | 0.584 | 0.649 | 0.640 |
| H7_unit_lgbm | B_MICU | 0.747 | 0.639 | 0.673 | 0.608 |
| H7_unit_lgbm | B_SICU | 0.774 | 0.656 | 0.610 | 0.660 |
| H7_unit_enet_lr | A_MICU | 0.728 | 0.533 | 0.635 | 0.562 |
| H7_unit_enet_lr | A_SICU | 0.643 | 0.577 | 0.510 | 0.541 |
| H7_unit_enet_lr | B_MICU | 0.753 | 0.645 | 0.643 | 0.567 |
| H7_unit_enet_lr | B_SICU | 0.736 | 0.703 | 0.654 | 0.659 |
| H7_route_lgbm | A_D | 0.792 | 0.746 | 0.686 | 0.552 |
| H7_route_lgbm | A_L | 0.725 | 0.688 | 0.620 | 0.587 |
| H7_route_lgbm | B_D | 0.789 | 0.701 | 0.657 | 0.624 |
| H7_route_lgbm | B_L | 0.691 | 0.644 | 0.632 | 0.647 |
| H7_route_enet_lr | A_D | 0.770 | 0.692 | 0.657 | 0.544 |
| H7_route_enet_lr | A_L | 0.705 | 0.664 | 0.626 | 0.549 |
| H7_route_enet_lr | B_D | 0.740 | 0.650 | 0.675 | 0.487 |
| H7_route_enet_lr | B_L | 0.645 | 0.590 | 0.575 | 0.642 |
