# plan_v4 (static 12-h task) — confirm (test), nboot 2000

| test | D [95% CI] | gap_within | gap_site | p (boot) | p (Holm) |
|---|---|---|---|---|---|
| H7_unit_lgbm | 0.023 [-0.021, 0.068] | 0.065 | 0.088 | 0.3250 | 0.6500 |
| H7_unit_enet_lr | 0.025 [-0.032, 0.081] | 0.065 | 0.091 | 0.3800 | 0.6500 |
| H7_route_lgbm | 0.032 [-0.001, 0.064] | 0.040 | 0.072 | 0.0530 | 0.1590 |
| H7_route_enet_lr | 0.054 [0.010, 0.098] | 0.053 | 0.107 | 0.0150 | 0.0600 |

| test | target | local | within-src | site-src | both |
|---|---|---|---|---|---|
| H7_unit_lgbm | A_MICU | 0.748 | 0.667 | 0.671 | 0.614 |
| H7_unit_lgbm | A_SICU | 0.720 | 0.669 | 0.612 | 0.558 |
| H7_unit_lgbm | B_MICU | 0.769 | 0.652 | 0.656 | 0.528 |
| H7_unit_lgbm | B_SICU | 0.681 | 0.669 | 0.628 | 0.618 |
| H7_unit_enet_lr | A_MICU | 0.711 | 0.641 | 0.619 | 0.539 |
| H7_unit_enet_lr | A_SICU | 0.662 | 0.630 | 0.530 | 0.545 |
| H7_unit_enet_lr | B_MICU | 0.696 | 0.601 | 0.640 | 0.543 |
| H7_unit_enet_lr | B_SICU | 0.711 | 0.646 | 0.626 | 0.641 |
| H7_route_lgbm | A_D | 0.759 | 0.723 | 0.651 | 0.628 |
| H7_route_lgbm | A_L | 0.648 | 0.687 | 0.614 | 0.599 |
| H7_route_lgbm | B_D | 0.789 | 0.617 | 0.655 | 0.612 |
| H7_route_lgbm | B_L | 0.679 | 0.687 | 0.667 | 0.653 |
| H7_route_enet_lr | A_D | 0.762 | 0.715 | 0.661 | 0.572 |
| H7_route_enet_lr | A_L | 0.661 | 0.677 | 0.499 | 0.587 |
| H7_route_enet_lr | B_D | 0.708 | 0.593 | 0.659 | 0.502 |
| H7_route_enet_lr | B_L | 0.679 | 0.612 | 0.563 | 0.634 |
