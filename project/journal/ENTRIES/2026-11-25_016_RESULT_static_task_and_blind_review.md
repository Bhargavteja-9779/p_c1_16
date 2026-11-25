# 2026-11-25 — RESULT: the static 12-h task does not confirm the site excess; blind review

**Blind novelty review.** A fresh agent saw only the results, plans and claim table, not my score. It gave 13/25 (differentiation 3, mechanism 2, evidence 3, breadth 2, significance 3). My score was 15. Under the rule the lower score counts. Its main objection is fair: the within-hospital controls are smaller covariate shifts than the site shift (domain AUC 0.71–0.97 vs 1.000), so "site > population" could just mean "bigger shift, bigger gap". It suggested a dose–response control, which became plan_v5.

**Static task (plan_v4, H7).** I ran the factorial on the published one-prediction-per-stay task (the protocol I reproduced for G4).
- Exploration was mostly null.
- I confirmed anyway, as pre-registered. Test, seeds 100–104 (tables/v4_confirm.md):
  - unit: D 0.023 [−0.021, 0.068] (LightGBM), 0.025 [−0.032, 0.081] (LR)
  - route: D 0.032 [−0.001, 0.064] (LightGBM), 0.054 [0.010, 0.098] (LR)
  - Holm p: 0.65, 0.65, 0.16, 0.06
- So 0 of 4 confirmed. All four point estimates are positive, in the same direction as the hourly task, but the test cells hold only about 25–60 septic stays each. Underpowered.

What I can honestly say is that the site excess is clearly shown for hourly early warning. For the static 12-h task it is not shown, with consistent but non-significant point estimates. In exploration, the unit shift alone cost as much as the site in the static task (within-hospital gap ≈ 0.10). In the static task the "population" component is relatively larger.

Budget note: the first v4 confirmation fit was killed by a worker restart after 64 of 80 jobs; that partial run's time (~5 min) is not in the ledger.
