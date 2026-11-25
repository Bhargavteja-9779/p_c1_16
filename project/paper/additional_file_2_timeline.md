# Additional file 2 — staged pre-specification timeline

Every plan is a versioned file in `experiments/`; analysis scripts were committed ("frozen") before the corresponding test-set run. Commit hashes refer to the project repository; times are UTC. "Known at the time" lists the outcome information already seen when the plan was written.

| Stage | Plan / freeze commit (date) | Hypotheses and test-set analyses | Known at the time | Deviations |
|---|---|---|---|---|
| 1 | plan_v1, plan_v2 + frozen analysis scripts — 641c403 (2026-11-24 22:26) | Site excess with ICU unit as contrast (primary; gradient boosting and logistic regression); label-free remedies; label-free estimators. Test run E6, seeds 100–104 | Validation results only (exploration seeds 0–2) | Label-free-remedy hypothesis changed from "share removed < 0.5" to an estimation target with a "reduction > 0" test after validation; source-role decomposition of the remedies added after the test result (post hoc) |
| 2 | plan_v3 (2026-11-25 00:24); analysis frozen and plan_v3b — 9e2e93b (01:03) | Age band and admission route as contrasts; feature-group contrast; size-matched training; pooled training (estimate) | Stage-1 test results | One bug fixed in the domain-classifier step before freezing (cell-defining variable excluded) |
| 3 | plan_v4 — fcc5d7e (02:24); script frozen and plan_v4b — 05f66d4 (02:33) | Static 12-h task, unit and admission-route contrasts | Stage-1 and stage-2 test results; stage-3 validation results (mostly null) | Age band excluded a priori as a weak contrast, based on stage-2 results |
| 4 | plan_v5 + analysis script — cb8eba8 (07:54) | Dose–response control (11 partitions); exploration on validation only in this manuscript | All earlier test results | Not run on the test set (exploratory only) |
| 5 | plan_v6 — 9ff10a7 (10:26) | Hypotension task across three databases; exploration on validation only in this manuscript | All earlier test results | Not run on the test set (exploratory only) |
| Post hoc | after simulated review round 1 | Pre-onset AUROC; sensitivity at 90% specificity | All results | Not pre-specified; labelled post hoc in the text |

Seeds 100–104 were fixed at project start and never changed. More than 300 validation evaluations of variants were logged (`state/variants_tried.csv` and an archived fork).
