# 2026-11-25 — RESULT: plan_v3 confirmation (test, seeds 100–104, analyze_v3.py frozen at 9e2e93b)

Files: results/analysis/v3_confirm.json, tables/v3_confirm.md, logs/analyze_v3_confirm.log. Holm runs across the 7 pre-specified tests.

**H4 confirmed, all 4 tests.** The cross-hospital gap exceeds the within-hospital gap for both new control factors:
- age, LightGBM: D 0.058 [0.045, 0.072]
- age, LR: D 0.091 [0.069, 0.113]
- route, LightGBM: D 0.023 [0.008, 0.038]
- route, LR: D 0.081 [0.056, 0.107]
- Holm p ≤ 0.006 for all four.

With E6 (unit), the site excess now holds against three different within-hospital population shifts. Caveat from exploration still stands: the age shift barely hurts (within-hospital gap 0.004), so age is a weak control. Route (0.026) and unit (0.045) are the informative ones.

**H5 not confirmed.** D_all − D_vitals = 0.018 [−0.001, 0.036], p 0.059, Holm 0.064. The descriptive picture matches exploration:
- process-only D = 0.046 [0.022, 0.070];
- vitals-only, labs-only and no-process D ≈ 0.008–0.009, all CIs include 0.

But the pre-specified contrast misses the bar. I will report the mechanism as suggestive, not confirmed. Validation had given 0.023 [0.002, 0.045]; the test effect is a bit smaller, the same shrinkage as for H1.

**H6 split by model.**
- LR: size-matched D 0.062 [0.030, 0.095], Holm 0.0035 — confirmed.
- LightGBM: 0.023 [0.002, 0.045], p 0.032, Holm 0.064 — not confirmed.

The LightGBM point estimate equals the full-size D (0.026). Subsampling removes training data, which widens the CI. It does not move the estimate towards 0. Even so, under the pre-registered rule this test fails, and I say so.

**E10.** Pooling the other hospital's same-unit data with local other-unit data: +0.012 [−0.000, 0.026] over the local other-unit model alone. External data adds little once local data from any unit exist.

Score so far: 9 of 10 pre-registered confirmatory tests across E6 + v3 passed in direction. Under Holm, 7 of 10 passed: E6 H1×2 and H2, plus v3 H4×4 and H6-LR. H5 and H6-LightGBM failed. H2 passed but is uninterpretable as a remedy (journal 012).
