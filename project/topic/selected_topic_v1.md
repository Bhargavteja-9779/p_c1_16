# Selected topic (cycle 1), DRAFT v1, 2026-11-24

**Working title:** Why sepsis early-warning models fail in a new hospital: the shift is in the outcome–feature relationship, so unlabelled fixes do not help and label-free performance estimates mislead.

## Problem
A hospital receiving an externally developed sepsis early-warning model needs to know two things: (i) how well it will work locally, and (ii) whether the drop can be fixed without labelling local patients. Critical Care's recent ML papers keep reporting internal→external drops (literature/reported_results.md, C1), but none explains where the drop comes from.

## Gap
- **WHAT EXISTS:**
  - Audits showing that missingness identifies the hospital (preprints202610.1449).
  - Comparisons of supervised adaptation strategies by target-data size (npj Digit Med 2026, doi:10.1038/s41746-026-02364-4).
  - Semi-supervised OT/alignment methods (JBHI 2023, WWW 2023).
  - General-ML shift-attribution methods: Cai, Namkoong & Yadlowsky, Oper Res 2025 (DISDE); Zhang et al., ICML 2023.
- **WHAT IS MISSING:** A demonstration, on open multi-site ICU data, of *which kind* of shift drives the sepsis transport failure. Is it case mix P(x), the measurement process, encoding/harmonisation, or P(y|x)? And the consequence: whether unlabelled-data remedies and label-free performance estimators can work at all.
- **WHY IT MATTERS:** If the shift is in P(y|x), a hospital cannot avoid labelling a local sample. The practical question becomes how small a labelled sample suffices to *verify* the model before go-live.

## Hypothesis (stated before the test)
H1: Most of the A↔B AUROC drop on PhysioNet 2019 is attributable to conditional shift. Unsupervised remedies close < 25% of the gap that pooled training closes.
H2: Label-free estimators of external AUROC have errors larger than the clinically relevant margin of 0.03 when sites are near-separable:
- internal validation
- importance weighting
- ATC
- DoC

H3: A small, stratified local labelled sample combined with a control-variate estimator built on the source model's scores gives external-AUROC estimates within ±0.03 at fewer labelled patients than naive local estimation.

## Research questions
- RQ1: How much of the drop is covariate/case-mix vs conditional shift? Answered with a decomposition (DISDE-style) plus the pooled-training bound.
- RQ2: Which unsupervised remedies help, and by how much?
  - drop process features
  - per-site normalisation
  - harmonisation repair
  - importance weighting
  - OT-style alignment
- RQ3: How wrong are label-free performance estimates?
- RQ4: How many labelled local patients does a reliable pre-deployment check need?
- RQ5: Does all of this replicate in another shift condition? Options: ICU unit (MICU↔SICU) within each hospital; eICU-CRD demo hospitals (mortality task); PhysioNet 2012 ICU types.

## Data (all open)
- PhysioNet/CinC 2019 (CC BY 4.0).
- eICU-CRD demo 2.0.1 (ODbL).
- PhysioNet 2012 challenge. Its license is still to be verified.

## Models and baselines
LightGBM, which matches the journal's dominant model class, plus logistic regression. Label-free estimators: internal AUROC, IW-AUROC, ATC, DoC. Local-label estimators: naive local AUROC vs the proposed estimator.

## Metrics
AUROC and AUPRC at hour and patient level; calibration slope and citl; for estimators, absolute error and coverage.

## Compute estimate
Each LightGBM fit takes about 1 min on 4 cores. About 400 fits ≈ 6–7 h, which is ≤ 15 h per cycle.

## Status
Novelty is NOT yet earned. RQ1/RQ3 need the closest DISDE-in-healthcare papers opened, and H3's estimator needs a prior-art check: "control variates AUROC estimation small labelled sample", "prediction-powered inference AUROC" (PPI, Angelopoulos et al. 2023, is close and must be checked).
