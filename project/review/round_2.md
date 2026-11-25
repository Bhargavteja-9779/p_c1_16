# Review round 2 (fresh reviewers, revised manuscript) — 2026-11-25

| Reviewer | Round 1 | Round 2 | Recommendation (round 2) |
|---|---|---|---|
| R1 Methods & statistics | 5/10 | 6/10 | Major revision. 20 numbers checked against result files, 0 substantive errors (2 rounding differences) |
| R2 Novelty & significance | 5/10 | 4/10 | Major revision; for *Critical Care* leans "reject with transfer" (suggests npj Digital Medicine, JAMIA, Diagnostic and Prognostic Research, Critical Care Explorations) |
| R3 Clarity & reproducibility | 5/10 | 6/10 | Major revision (borderline minor) |

G10 (two consecutive rounds of accept/minor) is NOT passed.

## Round-2 concerns and actions (text-only revision after round 2)
| Concern | Action |
|---|---|
| Title/claims imply D isolates a site component (R2) | Retitled "Cross-hospital versus within-hospital transfer…"; D described as not identified as a pure site effect; "template" removed |
| EmBER uses the same hospital × unit partitions (R2) | Stated explicitly; contribution = the gap contrast, not the partitioning |
| Gordaliza et al. arXiv:2512.09094 (crossed design in imaging) missing (R2) | Verified and cited |
| "Not detectable without labels" overreaches; only 3 estimators (R2) | Restricted to the estimators tested; ATC named as untested |
| Garg et al. miscited for chest radiographs (R2, R3) | Fixed |
| Pre-onset result should be co-primary for gradient boosting (R1) | Abstract and conclusions state that the gradient-boosting excess largely reflects recognition of established sepsis |
| Sensitivity threshold set on target labels; "one in eight" misread (R1, R3) | Threshold method stated in Methods; wording corrected (12.7 percentage points absolute, about a fifth relative); stated that real deployment would fare worse |
| Calibration reported selectively (R1) | Slope and calibration-in-the-large both reported; claim softened; no CIs stated |
| plan_v7 and plan_v1/v2 commit missing from timeline (R1) | Added to Additional file 2 |
| Third database possibly same hospital as A (R1) | Disclosed in Limitations |
| H2 framed as "criterion met" (R1, R2, R3) | Abstract: fixes did not improve transport; criterion (revised after validation) met only because within-hospital performance fell |
| Logistic regression deterministic; p floor (R1) | Stated |
| LOS partition mechanically tied to ICULOS feature (R1) | Stated |
| Cohort characteristics / excluded stays (R3) | Additional file 4 (per-cell characteristics incl. stays without unit) |
| Tables out of order (R3) | Renumbered |
| Repository reproduction path (R3) | README "Reproduce the manuscript" table mapping each table/figure to plan, frozen commit and command; requirements.txt |
| Ref 6 DOI (R2) | Added (verified) |

## Not done (would need new experiments or author action)
Source-transferred thresholds and lead-time analysis; repeated-split uncertainty; ATC/CBPE estimators; CIs for calibration contrasts; official TRIPOD+AI numbering with page/line locations; flow diagram; author declarations; public repository with DOI; a third independent hospital system.
