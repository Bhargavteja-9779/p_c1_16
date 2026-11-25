# Prior-art check: P5 (three-database factorial, site component) and P6 (SPRU)

Date: 2026-11-25. Searches: `scripts/prior_art.py` (OpenAlex + arXiv, logged in `state/novelty_ledger.json` → `queries`) plus web search. Opened papers are logged in `state/novelty_ledger.json` → `papers_opened` (15 entries added today). Earlier same-day queries under the claim IDs `P5`/`P6` (19 + 10) are also in the ledger and were not repeated.

## Queries used (this pass)

**P5_three_db_factorial (logged)**
1. site component case mix decomposition external validation intensive care unit type
2. within-hospital external validation different ICU unit versus different hospital
3. geographic versus temporal versus domain validation prediction model ICU
4. hospital effect beyond case mix prediction model discrimination loss
5. PhysioNet 2019 sepsis MICU SICU unit generalization
6. admission source subgroup shift versus hospital shift machine learning ICU
7. dose-response dataset shift magnitude AUROC drop clinical prediction
8. hypotension prediction ICU transfer between hospitals MIMIC PhysioNet 2019
9. measurement frequency hospital practice differences transportability ICU model
10. intra-hospital versus inter-hospital generalization deep learning electronic health records

Web search (not logged by the helper): "external validation performance drop different hospital versus different unit same hospital ICU prediction model eICU unit type"; "PhysioNet 2019 sepsis Unit1 Unit2 MICU SICU cross-unit generalization hospital A hospital B"; "variance decomposition hospital versus unit model performance AUROC external validation within-hospital control".

**P6_SPRU (logged)**
1. logistic recalibration model revision model extension updating methods comparison small validation sample
2. Bayesian dynamic updating clinical prediction model hierarchy closed testing
3. TrAdaBoost transfer boosting medical prediction small target sample
4. gradient boosting offset prior model initial prediction transfer learning tabular
5. model extension adding new predictors prediction model update few patients
6. residual model on top of existing clinical score boosting correction local
7. missingness indicators updating prediction model new hospital
8. few-shot adaptation sepsis prediction new hospital labelled patients
9. partial model update restricted features domain adaptation feature-level shift
10. stacked regression updating prediction model new setting

Web search (not logged by the helper): "boosting clinical risk score as offset add predictors residual offset boosting added predictive value Boulesteix"; "gradient boosting transfer learning initialize from source model predictions init_score base_margin target hospital clinical"; "site adaptation clinical prediction model update only missingness indicators measurement frequency features local hospital few labels".

## Papers opened (this pass)

| id | claim | read |
|---|---|---|
| doi:10.2196/99638 (JMIR Med Inform 2026, record density MIMIC-IV/eICU) | P5 | abstract |
| arXiv:2606.05365 (EmBER, environment-robust representation learning) | P5 | full text, partial (HTML) |
| doi:10.1038/s41746-026-02364-4 (npj Digit Med 2026, sepsis DL under distribution shift) | P5 | abstract |
| arXiv:2610.42126 (observation patterns, transportability under changing measurement) | P5 | abstract |
| doi:10.1038/s41598-020-67952-0 (Sci Rep 2020, sudden hypotension, multi-institution) | P5 | abstract |
| arXiv:2512.06511 (eICU diagnosis-specific mortality, XGBoost offset transfer) | P6 | full text (HTML) |
| doi:10.1177/0962280215626466 (Su et al. 2016, review of updating methods) | P6 | abstract |
| doi:10.1002/sim.7179 (Vergouwe et al., closed testing for updating) | P6 | abstract |
| doi:10.1186/1471-2105-11-78 (Boulesteix & Hothorn 2010, globalboosttest) | P6 | abstract + search summary |
| doi:10.1186/s12874-019-0802-0 (Volkmann et al. 2019, clinical offset + boosting/LASSO) | P6 | abstract |
| arXiv:2610.11162 (AutoAdapt, few-shot clinical adaptation) | P6 | abstract |
| doi:10.2196/38053 (TransferGBM, temporal drift, AKI) | P6 | abstract |
| doi:10.1016/j.jclinepi.2024.111636 (scoping review, updating AI-based CPMs) | P6 | abstract |
| doi:10.3389/fnagi.2022.966883 (TrGB, transfer GBM) | P6 | abstract |
| arXiv:2406.16484 (Robust prediction under missingness shifts) | P6 | abstract |

Relevant papers opened in earlier passes (see ledger, claim `P1_factorial_site_vs_population`), e.g. case-mix-corrected benchmarks (doi:10.1093/aje/kwq223, doi:10.1016/j.jclinepi.2014.06.018), propensity-weighted c-statistics (doi:10.1002/sim.9817), eICU cross-hospital generalisability (doi:10.1371/journal.pdig.0000023, arXiv:1812.02275), MIMIC ICU types as domains (doi:10.1109/bigdata.2018.8621927), and the Challenge description (doi:10.1097/ccm.0000000000004145), also bear on P5. Their summaries are in the ledger and are not repeated here.

## Claim → closest prior work → exact difference

| Claim | Closest prior work | Exact difference |
|---|---|---|
| P5 | doi:10.2196/99638: hospital vs unit-within-hospital variance decomposition in eICU (hospital eta2 0.354 vs unit 0.043 for HR record count) | It decomposes a measurement-process quantity, not the AUROC loss of a transported early-warning model, and has no transport experiment. |
| P5 | arXiv:2606.05365: PhysioNet 2019 environments defined as data source x ICU unit | It uses hospital x unit only as training/test environments for a robust-learning method and never compares cross-hospital vs cross-unit loss. |
| P5 | Case-mix benchmark / weighted c-statistic methods (doi:10.1093/aje/kwq223, doi:10.1002/sim.9817; earlier pass) | They separate case-mix from "model/site" effects statistically within one validation, not with a crossed hospital x unit within-hospital control across multiple databases and tasks. |
| P5 | doi:10.1038/s41746-026-02364-4 and the harmonised-ICU sepsis/AKI/mortality work (doi:10.1097/ccm.0000000000006359, earlier pass) | They report cross-database AUROC drops but have no within-hospital unit control or site vs case-mix decomposition. |
| P5 | arXiv:2610.42126: measurement-pattern features transfer less reliably across MIMIC/eICU | It is mortality and representation-level, without a unit x hospital factorial or hourly sepsis/hypotension tasks. |
| P6 | arXiv:2512.06511: source XGBoost log-odds as fixed offset + L1 logistic target correction | The target step is a lasso on all main effects, within one database across diagnosis groups; SPRU boosts a residual at a new hospital using only measurement-process + context features. |
| P6 | doi:10.1186/1471-2105-11-78 and doi:10.1186/s12874-019-0802-0: boosting with a fixed clinical model as offset | Same offset-boosting machinery, but used to test or add omics predictors in one dataset, not to repair cross-site transport with a restricted practice feature set. |
| P6 | doi:10.1177/0962280215626466, doi:10.1002/sim.7179: recalibration / revision / extension hierarchy and closed testing | Regression-coefficient updating; SPRU is a nonparametric (tree) partial revision restricted a priori to measurement-process terms. |
| P6 | arXiv:2610.11162 (AutoAdapt), doi:10.1038/s41746-026-02364-4 | Few-shot or small-target adaptation by recipe search, fine-tuning, retraining or DA for deep models; no feature-restricted residual boosting on source logits (from abstracts). |
| P6 | doi:10.2196/38053 (TransferGBM), doi:10.3389/fnagi.2022.966883 (TrGB) | GBM transfer by stacking two GBMs, or by instance reweighting that needs source data; neither uses an init_score offset with a restricted feature set. |

## Verdicts

**P5: partly done.**
- **Already established:** external-validation AUROC drops across ICU databases and hospitals (several papers, including on PhysioNet 2019 A/B). Unit/ICU type is used as a domain (MIMIC care units as domains; PhysioNet 2019 source x unit environments in arXiv:2606.05365). Statistical methods also separate case-mix from other validation-performance changes (case-mix-corrected benchmarks, weighted c-statistics, DISDE-type decompositions).
- **What I did not find:**
  - a crossed hospital x unit design in which cross-hospital same-unit transport is compared with same-hospital cross-unit transport as an internal control, with AUROC loss as the outcome;
  - such a design replicated across two tasks (hourly sepsis; MAP<65 within 6 h) and three public databases.
- **Closest published fact:** for a measurement-process variable (vital-sign record density), the hospital component is much larger than the unit-within-hospital component (doi:10.2196/99638). This supports the mechanism, but it is not the performance claim.
- **Novelty:** it lies in the design and the empirical finding, not in a new method.
- **Reviewer risk: moderate.**
  - Reviewers will cite case-mix benchmark methods and the eICU multi-hospital literature and ask why a formal decomposition (membership model, weighted c-statistic) was not used.
  - The claim "a site component beyond case mix" is only partly identified by a unit control: units are not the only case-mix axis.
  - PhysioNet 2012 vs 2019 also differ in extraction and label definitions.
  - The "dose-response vs shift size" angle was not found in prior work either. Without it, or controls such as admission route, age and random halves, the claim will look thin.

**P6 (SPRU): partly done. The components are prior art; the specific combination appears novel.**
- **Prior art for the components:**
  - Updating an imported model with local data via an offset is standard: the Steyerberg/Vergouwe/Su hierarchy and closed testing.
  - Boosting on top of a fixed model's linear predictor as an offset exists (globalboosttest; Volkmann et al. 2019).
  - Using a source XGBoost's log-odds as an offset and fitting a target-specific correction is published for ICU mortality (arXiv:2512.06511).
  - init_score / base_margin warm-starting is a well-known engineering practice; I found no citable paper for it in the clinical transfer setting.
- **What I did not find:** a residual updater restricted a priori to measurement-process features (time since last measurement, measurement counts) plus context, motivated as repairing a site/practice component, evaluated at 50–400 local patients for ICU sepsis/hypotension, and compared against source-only, local-only, pooled and unrestricted residual updating.
- **Reviewer risk: moderate to high.**
  - A reviewer can fairly call SPRU "model extension / partial revision with an offset, implemented in LightGBM", which is a known idea.
  - arXiv:2512.06511 is the most direct precedent for the offset + target correction structure.
  - The contribution must therefore be framed as the restriction hypothesis (which terms to update), and must be shown to beat the unrestricted residual update and simple recalibration (intercept/slope) at small n. Otherwise it reduces to known updating.
  - AutoAdapt (arXiv:2610.11162) and the npj sepsis paper (doi:10.1038/s41746-026-02364-4) will be raised as few-shot or small-target baselines. Their details were read only at abstract level (UNVERIFIED beyond the abstract).
