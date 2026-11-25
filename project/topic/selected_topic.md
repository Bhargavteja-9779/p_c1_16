# Selected topic (cycle 1), v2, 2026-11-24 (v1 kept in selected_topic_v1.md)

**Working title:** How much of a sepsis model's failure in a new hospital is about the hospital? A factorial (ICU unit × hospital) transport analysis on open multi-site ICU data.

## Problem
Critical Care's recent ML papers report internal→external drops but cannot say where they come from (literature/reported_results.md C1). For a hospital adopting a model, two things are different:
- a *population* difference (different case mix, as between a medical and a surgical ICU in the same hospital);
- a *site* difference (charting resolution, measurement process, coding, label-generating practice).

Only the population part is expected to shrink by choosing a model trained on similar patients. The site part needs local data.

## Gap
- **WHAT EXISTS:** missingness-identifies-hospital audits (preprints202610.1449); supervised adaptation comparisons by target size (npj Digit Med 2026); general-ML attribution methods (DISDE, Oper Res 2025; Zhang et al., ICML 2023). The general-ML methods rely on covariate overlap.
- **WHAT IS MISSING:** an overlap-free estimate of the site component of transport loss. Here overlap does not exist: domain AUC 0.9996, and even vitals-only gives 0.978. Also missing: a test of which site ingredients unlabelled fixes can remove.
- **WHY IT MATTERS:** it tells adopters whether a "similar-population" model will do, or whether local labelled data is unavoidable.

## Hypotheses (fixed before confirmation)
- H1 (primary): the transport gap for a different hospital and the same unit exceeds the gap for the same hospital and a different unit. Paired over transfer pairs, CI excludes 0, Holm-corrected.
- H2: unlabelled site fixes together remove less than half of the site component:
  - harmonisation repair
  - removal of process features
  - per-site quantile normalisation
- H3: label-free estimates of transported AUROC have absolute error > 0.03 in most off-diagonal transfers. Estimators: internal AUROC, importance weighting, ATC, DoC.

## Research questions
- RQ1: size of the population (unit) and site components, overall and by direction.
- RQ2: which site ingredients unlabelled fixes can remove.
- RQ3: reliability of label-free estimates, and how many labelled local patients existing estimators (classical, PPI-style) need for ±0.03.
- RQ4: does it hold for two model classes (LightGBM, logistic regression), patient-level metrics, AUPRC and calibration?
- RQ5 (breadth): a second dataset if feasible (eICU-CRD demo; mortality; hospital × unit-type). Otherwise stated as a limitation.

## Data
- PhysioNet/CinC 2019, hospital systems A and B, units MICU and SICU (CC BY 4.0). Patients with unknown unit are excluded from cell analyses.
- eICU-CRD demo 2.0.1 (ODbL) for RQ5.

## Contribution type
A (failure mode demonstrated with data) + D (factorial transport protocol, released with code). **G5 interpretation (logged as D16):** this is not a method-beats-baseline paper. The G5 standard (confirmation seeds, Holm p < 0.05, effect size, CI excluding 0) is applied to H1.

## Compute
4 cells × 2 model classes × 5 confirmation seeds = 40 fits for the main matrix, plus ablations (~120 fits) and the estimator study (cheap). That is about 3–4 h of CPU.
