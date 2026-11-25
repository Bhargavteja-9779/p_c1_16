# Review round 1 (simulated panel, fresh context) — 2026-11-25

Panel: R1 methodology & statistics, R2 novelty & related work, R3 clarity/reproducibility/fit. Each reviewer saw only the manuscript, additional files, result files and code (not the research log or decisions).

| Reviewer | Score | Recommendation |
|---|---|---|
| R1 Methods & statistics | 5/10 | Major revision |
| R2 Novelty & related work | 5/10 | Major revision (may fit an informatics journal better) |
| R3 Clarity, reproducibility, fit | 5/10 | Major revision |

R1's number check: 12 numbers verified against result files, all consistent. Two reporting errors found: the dose–response residual quoted was the sensitivity analysis, not the primary; patient-level CIs used 400 rather than 2,000 resamples.

## Triage of MAJOR concerns and actions

| # | Concern (source) | Type | Action taken |
|---|---|---|---|
| 1 | Abstract/conclusions overreach; generality from one hospital pair (R2, R3) | writing | Title, abstract and conclusions restricted to "these two hospital systems, hourly sepsis"; task- and model-dependence stated in abstract |
| 2 | Missing closest prior work: EmBER arXiv:2606.05365, JMIR doi:10.2196/99638, adversarial domain separation doi:10.1109/BigData50022.2020.9378058 (R2) | writing | All three verified (Crossref/arXiv) and cited with stated differences |
| 3 | Missing clinical transport literature (Epic sepsis model, myth of generalisability, Moor 2023) (R2) | writing | Verified and cited in Background |
| 4 | Clinical meaning of AUROC differences; calibration and AUPRC (pre-specified secondary) not reported (R1, R3) | evidence | Added: calibration slope/intercept and AUPRC by transfer type (pre-specified, scripts/secondary_E6.py); sensitivity at 90% specificity (post hoc, scripts/clinical_metrics.py); Table 4 |
| 5 | Hour-level AUROC rewards recognising established sepsis (R1) | evidence | Added post-hoc pre-onset AUROC. Result reported honestly: site excess remains for logistic regression (0.059, 0.027–0.094) but not for gradient boosting (0.019, −0.006 to 0.041) |
| 6 | H2 reinterpretation presented as primary (R1, R2, R3) | writing | Pre-specified result reported first (criterion met); decomposition labelled post hoc |
| 7 | Dose–response reported selectively (R1) | writing (error) | Primary symmetric-KL residual now reported first; both labelled exploratory; LOS partition result in Results and Limitations |
| 8 | Pre-registration overstated (R1, R3) | writing | "Staged pre-specification" wording; Additional file 2 timeline with commit, date and what was known; deviations listed |
| 9 | D confounds site with between-hospital case mix / source learnability (R1, R3) | writing | D described as an upper bound on the site component; "both" cells and per-role AUROC reported (Table 4). Full 2×2 interaction model and training-split resampling NOT done (stated as limitation) |
| 10 | Uncertainty ignores training variability (R1) | partial | Seed SDs reported; conditioning on one split stated in Methods and Limitations; repeated-split analysis not done |
| 11 | No reporting checklist (R3) | writing | Additional file 3 (TRIPOD+AI mapping, gaps marked) |
| 12 | Reproducibility gaps (R3) | code/doc | requirements.txt with pinned versions; README self-contained for both datasets; audit/figure commands listed. Public repository with DOI: authors' action |
| 13 | Placeholder declarations; AI-use oversight (R3) | authors | Structure kept; must be completed by the human authors (cannot be done by the assistant) |
| 14 | Preprint comparator characterised from abstract (R2) | writing | Labelled as approximate and abstract-based; preprints marked as such in references |

## MINOR concerns addressed
Uncited references removed or cited; bootstrap description corrected (2,000 hour-level, 400 patient-level; p floor explained); narrative of first idea removed from Background; hypothesis codes replaced by descriptive names; Figure 1 (forest plot) added; Additional file 1 given a legend for internal labels; exclusion of stays without unit stated (39%) and included in other contrasts; LightGBM missing-data handling and hyperparameters stated; admission-route/ICU-LOS non-circularity stated; label generation as a possible site component stated.

## Not addressed (stated as limitations or author actions)
- Repeated-split / training-bootstrap uncertainty; full 2×2 interaction model.
- Flow diagram and per-cell patient-characteristics table.
- Challenge utility score; lead-time-stratified AUROC beyond the pre-onset restriction.
- Full text of the preprint comparator.
- Author declarations, public repository URL/DOI.
