# 2026-11-25 — HYPOTHESIS (before any v6 model): does the site excess survive a new task and a third database?

The blind reviewer gave 13/25. The weakest point is breadth: everything rests on one dataset (PhysioNet 2019) and one task (sepsis early warning). On the second task I tried, the static 12-h sepsis prediction, the result was underpowered.

Today I checked two facts I had not verified before:
- The 2019 challenge paper (full text, PMC6964870) names hospital system A as Beth Israel Deaconess and B as Emory.
- The 2012 challenge data comes from MIMIC-II (Silva 2012 abstract), which was collected at "a tertiary care hospital" between 2001 and 2007 (Saeed 2011 abstract).

All three databases record MICU and SICU stays. So I can cross three sites with two units on a task whose label exists in all three: hypotension (MAP < 65 mmHg) within the next 6 hours. Chiang et al. 2025 in Critical Care is the clinical anchor for this kind of early warning.

What I expect, written before running anything (plan_v6):
- **H9:** moving to another hospital with the same unit costs more AUROC than moving to the other unit in the same hospital. That is, D9 > 0 for LightGBM and LR.
- **H9b:** D9 > 0 holds for each site pair separately.
- **H9c:** part of the excess disappears when measurement-process features are removed.

What would prove me wrong: D9 ≈ 0 or < 0. That would mean that for hypotension, a physiology-driven label, case-mix dominates and the sepsis result is task-specific. I would report that.
