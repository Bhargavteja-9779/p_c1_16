# 2026-11-25 — RESULT: plan_v3 exploration (validation, seeds 0–2)

Numbers: tables/v3_explore.md, results/analysis/v3_explore.json.

**The site excess survives every control factor I tried.** The within-hospital gap depends on the control:
- age band: 0.004 for LightGBM (basically nothing)
- admission route: 0.033
- ICU unit: 0.035

The cross-hospital gap stays around 0.067–0.078 whatever the control. So D is 0.063 (age), 0.036 (route) and 0.043 (unit) for LightGBM, larger for LR, and every CI excludes 0.

I had hoped age would be a strong population shift. It is not. A model trained on older patients works almost as well on younger ones in the same hospital. That makes the age comparison easy, so I will not lean on it in the paper. Route and unit are the informative controls.

**Mechanism: my prediction was half right.**
- All-feature D is 0.043.
- Vitals-only, labs-only and no-process models all give D around 0.02, with CIs touching 0.
- Process-only gives the largest D, 0.056.
- The pre-specified D_all − D_vitals = 0.023 [0.002, 0.045].

So the measurement-process features carry the site-specific part, but labs on their own do not. This also fits journal 012: removing process features shrank D in E6, and it did so by making the model worse inside its own hospital too. Process features are useful at home, and they are the part that does not travel.

**Size does not explain it.** With every source cell subsampled to the same number of patients, D is 0.043 (LightGBM) and 0.055 (LR).

**Pooling helps little.** Adding the other hospital's same-unit data to the local other-unit data improves AUROC by 0.010 [−0.002, 0.023].

**G4 surprise (good):** re-implementing the closest published protocol gave almost the same cohort (30,629 vs 30,646 stays) and the same A→B drop (−0.115 vs −0.117).

One bug caught before freezing: the domain classifier for age/route had been given the variable that defines the cells. I fixed it, froze the script (9e2e93b), and launched the confirmation.
