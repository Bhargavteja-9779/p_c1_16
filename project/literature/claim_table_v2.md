# Claim table v2: prior-art check (2026-11-24)

The searches are logged in `state/novelty_ledger.json` under `queries`: 17 for P1, 11 for P2 and 14 for P3, from OpenAlex, arXiv and web search. The papers read are logged under `papers_opened`: 43 new entries, of which 9 were read in full text (methods and results sections) and the rest from the abstract. Every DOI was checked against Crossref or DataCite, and every arXiv ID against the arXiv API.

---

## P1_factorial_site_vs_population

**Verdict: the design appears novel; the goal has been partly done before.** Separating "case-mix" from "model/site" effects in external validation is an old and well-established aim:
- Vergouwe 2010, doi:10.1093/aje/kwq223
- Debray 2014, doi:10.1016/j.jclinepi.2014.06.018
- doi:10.1371/journal.pone.0148820
- doi:10.1002/sim.9447
- doi:10.1002/sim.9817

General-ML methods decompose a performance gap into p(X) and p(Y|X) parts:
- DISDE, doi:10.1287/opre.2023.0217
- arxiv:2210.10769
- arxiv:2402.14254

Every one of these methods needs covariate overlap, through density ratios, propensity scores or positivity, or else a model-based benchmark. doi:10.1002/sim.9817 states outright that propensity standardisation is unbiased only when positivity holds. We found **no paper** that uses a crossed ICU-unit × hospital design as an overlap-free control to split a transport gap into site and population parts, on PhysioNet 2019, eICU, MIMIC or any other ICU data.

| Closest prior work | Exact difference |
|---|---|
| doi:10.1002/sim.9817: propensity-standardised c-statistic separating case mix from lack of generalisability | It reweights for case mix and needs positivity. We have no overlap (domain AUC ≈ 0.98–1.0), so we use a design contrast instead: the same hospital with a different unit, compared with a different hospital and the same unit. |
| doi:10.1287/opre.2023.0217 (DISDE), with arxiv:2210.10769 and arxiv:2402.14254 | They attribute the gap to p(X) and p(Y\|X) terms through a domain classifier or importance weights on shared support. That support does not exist here, and none of them separates *site* from *population* using a within-hospital unit control. |
| doi:10.1097/ccm.0000000000006359: ricu-harmonised AUMCdb/HiRID/eICU/MIMIC transfer | It reports drops of up to 0.20 and notes that the unit mix differs (MICU 65–79% in the US datasets, SICU 72% in AUMCdb) and that this confounds validation. It recommends an "oracle" model but never separates the components; in its design, dataset and unit type are confounded. |

The nearest *design* analogue is in another field. arxiv:2512.09094 uses a crossed centre × annotator design for MS-lesion segmentation, attributing the gap through Shapley values on a causal graph.

### Within-hospital unit vs. between-hospital comparisons on PhysioNet 2019, eICU or MIMIC
- **arxiv:2609.30781** (2026) evaluates across eICU hospitals and, *separately*, across six care units within one MIMIC-IV hospital. The two are different datasets, not a crossed design, and the target is conformal coverage, not AUROC. This is the only paper we found that puts both kinds of shift side by side.
- **doi:10.1109/bigdata.2018.8621927** (MIMIC ICU types as domains) and **arxiv:1806.02878** (MIMIC care-unit heterogeneity) look at within-hospital unit shift only.
- **doi:10.1093/jamia/ocad174** compares tertiary with community ICUs within one health system (Northwestern) and also uses MIMIC. It attributes the poor MIMIC transport to case mix informally, with no crossing and no estimated components.
- **doi:10.1097/ccm.0000000000004145** (the PhysioNet 2019 Challenge paper) reports only that generalising across hospital systems is hard. We found **no paper** that analyses MICU vs SICU within hospital systems A and B of PhysioNet 2019.

---

## P2_unlabelled_fixes_site_component

**Verdict: partly done.** Several parts are already published:
- Label-free and target-unlabelled remedies mostly fail on ICU shift: doi:10.1038/s41598-022-06484-1 (UDA and DG fail under temporal shift, MIMIC-IV), doi:10.1145/3450439.3451878 (DG fails on eICU), and doi:10.1097/ccm.0000000000006359 (DG fails across datasets). Anchor regression gives only modest gains (doi:10.1093/rssdat/udag001).
- Removing measurement-process features **reduces the cross-database drop**. doi:10.64898/2026.04.05.26350209 (MIMIC-IV → eICU sepsis mortality): with logistic regression the drop is −0.047 without measurement counts and −0.082 with them; gradient-boosted trees show a smaller incremental effect (abstract wording; "reversed" not verified). The missingness audit doi:10.20944/preprints202610.1449, already in the ledger, shows the same on PhysioNet 2019 A→B.
- Aggregating features into clinical concepts reduces shift caused by a record-system change (arxiv:1908.00690).

**Not done:** measuring *what fraction of an isolated site component* each label-free fix removes. That needs a site component identified by design, which comes from P1.

| Closest prior work | Exact difference |
|---|---|
| doi:10.64898/2026.04.05.26350209: measurement counts and the eICU drop | It compares model specifications with and without counts against the total internal→external drop. It has no unit control, so it cannot say how much of the *site* part the removal fixes, and it does not test harmonisation or per-site normalisation. |
| doi:10.1093/rssdat/udag001: anchor regression and boosting across 9 ICU databases | This is multi-source domain generalisation with dataset-ID anchors, plus regimes that need target labels. It does not use single-source label-free fixes and does not isolate a site component. |
| doi:10.1038/s41598-022-06484-1 and doi:10.1145/3450439.3451878 | UDA and DG fail, but under temporal or induced shifts, and are measured on total OOD performance rather than on a site component isolated by design. |

---

## P3_label_free_performance_estimation_clinical

**Verdict: partly done.** Label-free estimators have been tested on clinical data, but only on **imaging**:
- arxiv:2507.22776 extends ATC, DoC and CBPE to confusion-matrix and AUC estimation on chest X-ray and finds systematic failures under prevalence shift.
- doi:10.1016/j.media.2026.104364 (MOVAL) estimates performance on medical images.

On structured EHR data, doi:10.1038/s41746-024-01414-z estimates external AUROC from external *summary statistics* across 5 US data sources, with a 95th-percentile AUROC error of 0.03. That is the closest clinical tabular result. Whether it uses outcome summary statistics is UNVERIFIED from the abstract. We found **no** evaluation of ATC, DoC or importance-weighted AUROC estimation on multi-hospital ICU or sepsis EHR data, and none under near-zero covariate overlap.

| Closest prior work | Exact difference |
|---|---|
| arxiv:2507.22776: ATC/DoC/CBPE confusion-matrix and AUC estimation, chest X-ray | Imaging with real and simulated shift. We evaluate on ICU tabular time series across hospitals and units with domain AUC ≈ 1, and add importance weighting. |
| doi:10.1038/s41746-024-01414-z: external AUROC from summary statistics, 5 US sources | It reweights the internal cohort to external *statistics*, which assumes those statistics are shared. It does not test confidence-based estimators or a no-overlap ICU setting. |
| arxiv:2201.04234 (ATC) and doi:10.52202/085713-5379 (PAPE) | The methods themselves, benchmarked on vision/text and census data. ATC's own theory says no estimator can be valid without assumptions about the shift; we measure the error on clinical sites. |

---

## Uncertain points
- doi:10.1038/s41746-024-01414-z: whether its summary statistics include outcome information is UNVERIFIED (only the abstract was read).
- doi:10.1093/jamia/ocad174: whether the "community ICUs" are separate hospitals within the same system was not checked in the full text.
- Several 2026 preprints were read from the abstract only: arxiv:2608.12885, arxiv:2605.11284 and doi:10.64898/2026.07.19.26358409.
