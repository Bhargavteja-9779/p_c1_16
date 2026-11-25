# plan_v5 dose-response — explore

| test | residual [95% CI] | p (boot) |
|---|---|---|
| H8_kl_ols | -0.076 [-1.524, 0.032] | 0.3950 |
| H8sens_auc_ols | 0.016 [-0.065, 0.059] | 0.4680 |
| H8sens_kl_iso | -0.023 [-0.130, 0.056] | 0.7670 |
| H8sens_auc_iso | 0.023 [-0.032, 0.057] | 0.3760 |

H8b: mean site gap 0.069 vs largest within-partition mean gap 0.197 (los); holds=False; partition-bootstrap P = 0.348

Shift-size ranges: {"within": {"kl": [-0.019563074878623188, 8.397192718317736], "auc": [0.48884874083978425, 0.9677916009393881]}, "site": {"kl": [19.957609864122126, 22.815826740572287], "auc": [0.9993494630067321, 0.9999647749449222]}}
Within-hospital corr(gap, S): {"kl": 0.18165318363120173, "auc": 0.18662952768907162}

| partition | within mean gap | site mean gap |
|---|---|---|
| age | 0.004 | 0.067 |
| age50 | 0.005 | 0.068 |
| age75 | 0.012 | 0.068 |
| los | 0.197 | 0.062 |
| rand1 | 0.005 | 0.075 |
| rand2 | 0.007 | 0.069 |
| rand3 | 0.005 | 0.067 |
| route | 0.033 | 0.069 |
| route6 | 0.029 | 0.066 |
| sex | 0.008 | 0.070 |
| unit | 0.035 | 0.078 |
