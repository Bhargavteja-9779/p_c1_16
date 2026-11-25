# Additional file 3 — TRIPOD+AI checklist (abridged mapping)

Status: Reported / Partly reported / Not reported (with reason). Section names refer to the manuscript.

| Item | Topic | Status | Where / note |
|---|---|---|---|
| 1 | Title identifies a prediction-model study and the target population | Reported | Title |
| 2 | Structured abstract | Reported | Abstract (≤ 350 words) |
| 3a–b | Background, rationale, objectives | Reported | Background |
| 4 | Study design (retrospective, staged pre-specification) | Reported | Methods; Additional file 2 |
| 5a–b | Data source, dates, setting | Partly reported | Methods: PhysioNet/CinC 2019; calendar dates of care not available in the open data |
| 6a–c | Participants, eligibility, treatments | Partly reported | Methods: cohort definition; exclusion of stays without unit (39%); treatment information not available |
| 7 | Data preparation, harmonisation | Reported | Methods; label-free remedies |
| 8a–b | Outcome definition, blinding | Reported | Challenge SepsisLabel (6 h before onset); label generation is site-specific (Limitations) |
| 9a–c | Predictors, measurement, timing | Reported | Methods: 134 features from data up to each hour |
| 10 | Sample size | Partly reported | Fixed by the open dataset; no a-priori power calculation; static task underpowered (stated) |
| 11 | Missing data | Reported | LightGBM native handling; logistic regression median imputation + indicators |
| 12a–g | Analysis: model types, tuning, evaluation, calibration, fairness | Partly reported | Tuning budgets equal; calibration slope/intercept reported; subgroup/fairness analyses by sex and age reported only as transfer contrasts, not as fairness metrics |
| 13 | Class imbalance | Reported | No resampling; AUPRC reported |
| 14 | Fairness | Not reported | Out of scope; stated as limitation of reporting |
| 15 | Model output, thresholds | Partly reported | Risk scores; post-hoc threshold at 90% specificity |
| 16 | Training vs evaluation differences | Reported | Factorial design |
| 17 | Ethics | Partly reported | Public de-identified data; author statement pending |
| 18 | Funding, conflicts | Not yet reported | Placeholder — authors to complete |
| 19 | Protocol / registration | Partly reported | Version-controlled staged plans (Additional file 2); no public registry |
| 20 | Data sharing | Reported | Open data; code repository (URL to be completed) |
| 21 | Code availability | Reported | Repository; requirements.txt pins package versions |
| 22 | Patient and public involvement | Not reported | None |
| 23a–b | Participants: flow, characteristics | Partly reported | Cell sizes and events in Methods; per-cell characteristics table and flow diagram not yet included |
| 24 | Model development details | Reported | Methods; hyperparameter grids |
| 25 | Model specification | Partly reported | Code released; no single deployable model is proposed |
| 26 | Performance with CIs | Reported | Tables 1–4, Figure 1 |
| 27 | Model updating | Not applicable | — |
| 28 | Interpretation, limitations | Reported | Discussion |
| 29 | Usability in current care | Partly reported | Discussion: implications for local verification |
