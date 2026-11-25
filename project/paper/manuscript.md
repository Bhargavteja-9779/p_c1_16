---
title: "How much of a sepsis early-warning model's failure in a new hospital is about the hospital? A pre-registered factorial transport analysis on open multi-site ICU data"
article_type: Research
journal: Critical Care
status: DRAFT for submission — author names, affiliations, ethics/funding statements to be completed by the authors
---

# How much of a sepsis early-warning model's failure in a new hospital is about the hospital? A pre-registered factorial transport analysis on open multi-site ICU data

**Authors:** [to be completed by the authors]
**Corresponding author:** [to be completed]

## Abstract

**Background.** Machine-learning early-warning models for sepsis lose accuracy when moved to another hospital, but external-validation studies cannot say how much of the loss comes from the new *hospital* (charting, measurement practice, coding) and how much from different *patients* (case mix). The distinction matters to an adopting hospital: case-mix loss can be reduced by choosing a model trained on similar patients, site loss cannot. Overlap-based decomposition methods fail here because the hospitals are almost perfectly separable from their data.

**Methods.** We used the open PhysioNet/Computing in Cardiology 2019 data (two hospital systems, 40,336 ICU stays) and a factorial design: models trained in one hospital × ICU-unit cell were evaluated in the same unit of the other hospital (site transfer) and in the other unit of the same hospital (population transfer, identical data encoding). The site excess D is the site-transfer AUROC loss minus the population-transfer loss. Hypotheses, models, seeds and analysis code were fixed before the test set was used; inference used a patient-cluster bootstrap over five confirmation seeds with Holm correction. We additionally tested label-free remedies, label-free performance estimators, two further within-hospital control factors (age band, admission route), feature groups, size-matched training and a second (static 12-h) prediction task.

**Results.** For hourly sepsis prediction, moving to the other hospital cost more than moving to the other unit: D = 0.026 AUROC (95% CI 0.005–0.049; Holm p = 0.018) for gradient boosting and 0.063 (0.031–0.098; Holm p = 0.0015) for logistic regression, positive in all four target cells. The site excess also exceeded the loss from an age-band shift (D 0.058 and 0.091) and an admission-route shift (D 0.023 and 0.081; all Holm p ≤ 0.006). Label-free remedies did not improve transported AUROC (0.763 to 0.762); they shrank D only by degrading within-hospital performance. Label-free AUROC estimates missed the transported AUROC by more than 0.03 in 77–100% of transfers. Models restricted to measurement-process features showed the largest site excess (0.046, 0.022–0.070), but the pre-specified mechanism contrast was not significant. In the static 12-h task, point estimates pointed the same way (0.023–0.054) but none of four tests survived correction.

**Conclusions.** In these two hospitals, part of the transport loss of an hourly sepsis model is specific to the site and cannot be removed by picking a similar-population model, by unlabelled harmonisation, or estimated without local labels. A hospital adopting such a model should plan for local labelled verification.

**Keywords:** sepsis; early warning; machine learning; external validation; transportability; dataset shift; intensive care unit

## Background

Early-warning models for sepsis are increasingly built from routinely charted ICU data, and the central weakness reported for them is transport: performance measured in the development hospital is not reproduced elsewhere. In the PhysioNet/Computing in Cardiology Challenge 2019, the organisers concluded that generalising to different hospital systems remained a challenge [1]. Recent studies on the same open data report that a gradient-boosting model's AUROC fell from 0.725 internally to 0.608 after transfer from hospital system A to B [2]. In recent *Critical Care* ML papers, internal-to-external drops of up to 13.8% AUROC are reported when a model is trained on a single distinctive source [3].

These numbers say that a model loses accuracy, not why. For an adopting hospital there are two different reasons with different remedies. A *population* difference — a surgical rather than a medical ICU, older patients, different admission routes — can in principle be addressed by choosing or training on more similar patients. A *site* difference — how often variables are measured, assay and unit conventions, resolution of charted values, local practices behind the sepsis label — travels with the hospital, whatever the patients. Classical external-validation frameworks separate case mix from incorrect coefficients using benchmark values or membership models [4, 5], and propensity-based standardisation adjusts discrimination for case mix [6]. Machine-learning attribution methods split a performance gap into covariate and conditional components [7–9]. All of these need the two populations to overlap in covariate space. Between the two PhysioNet 2019 hospitals they do not: a classifier separates them with AUC above 0.99 from the data alone, even from vital signs only, because of charting resolution and encoding differences.

Our first project idea was to show that measurement patterns act as a hospital "shortcut". A search before any modelling found this had just been shown on the same data [2], so we dropped it. A diagnostic analysis then showed that the drop between the hospitals is mostly a change in the relation between features and outcome that unlabelled corrections barely touched, and that density-ratio decomposition was infeasible. What remained possible was a control that needs no overlap: transferring a model between ICU units *within* a hospital, where data encoding is identical, gives an empirical yardstick for a population shift. Crossing hospital with unit gives a factorial design in which the site excess can be estimated directly.

We asked: (1) Is the loss from moving to another hospital larger than the loss from moving to another population within the same hospital, and does this hold for different definitions of "another population"? (2) Can label-free remedies remove the site component? (3) Can the transported performance be estimated without local labels? (4) Which feature groups carry the site component, and does it hold for a second prediction task?

## Methods

### Data and cohort
We used the training set of the PhysioNet/Computing in Cardiology Challenge 2019 (CC BY 4.0) [1]: hourly records of 40,336 ICU stays from two US hospital systems (A: 20,336 stays; B: 20,000), with 40 vital-sign, laboratory and demographic variables and the Challenge sepsis label (SepsisLabel, Sepsis-3 based, shifted 6 h before onset) [1]. All 40,336 files were validated (41 columns, contiguous hourly ICU length of stay). Stays with a recorded unit (MICU or SICU) formed four cells: A-MICU, A-SICU, B-MICU, B-SICU (24,719 stays; 940,250 patient-hours; 1,616 stays with sepsis). Stays without a recorded unit were excluded from the cell analyses.

### Splits and leakage control
Within each hospital, patients were split 60/20/20 into training, validation and test sets, stratified by sepsis status, with a fixed seed chosen before modelling; the split file is versioned with the code. Test cells contained 1,056–1,400 patients (48–115 with sepsis). An automated leakage check confirmed: no patient in more than one split or cell, no duplicated patient time series, no look-ahead in features (rebuilding features from records truncated at a random hour reproduced the full-record features exactly in 200 of 200 sampled patients), no label or identifier among the features, and model fitting and selection restricted to source-cell training and validation rows.

### Features and models
Each patient-hour was represented by 134 features computed from data available up to that hour: last observed value of each variable, 6-h rolling mean/min/max and 6-h change for vital signs, measurement-process features (hours since last measurement and number of measurements in the past 24 h per variable), and age, sex, ICU length of stay so far and time from hospital to ICU admission. We used gradient-boosted trees (LightGBM; number of leaves chosen from {15, 63, 255} with early stopping on source validation AUROC) and L2-regularised logistic regression (median imputation, missingness indicators, C chosen from {0.01, 0.1, 1}); both had the same tuning budget of three configurations.

### Factorial transport design
For target cell t, the *local* model was trained in t, the *population-transfer* source in the other unit of the same hospital, and the *site-transfer* source in the same unit of the other hospital. With gap = AUROC(local) − AUROC(transferred), all evaluated on t's test patients, the site excess is

D(t) = gap_site(t) − gap_population(t) = AUROC_t(population source) − AUROC_t(site source),

so the local model cancels. The primary statistic is D averaged over the four target cells and five confirmation seeds (hour-level AUROC); patient-level AUROC (maximum risk per stay) was secondary.

### Additional experiments
- **Label-free remedies (H2):** harmonisation of encoding artefacts found in the diagnosis (calcium values below 2 in B treated as a different assay and set missing, age rounded, EtCO2 removed); removal of measurement-process features; per-hospital quantile normalisation fitted on unlabelled training rows.
- **Label-free performance estimation (H3):** internal AUROC, model-implied AUROC and importance-weighted AUROC, compared with the observed transported AUROC; and a split-half check of how many labelled local patients give an AUROC estimate within ±0.03.
- **Other control factors (H4):** age band (<65 vs ≥65 years) and admission route (ICU admission within 24 h of hospital admission vs later) replaced ICU unit as the within-hospital factor (all patients).
- **Mechanism (H5):** models restricted to vital signs, laboratory values, all-but-process or process-only features.
- **Size-matched training (H6):** every source cell subsampled to the smallest cell's number of patients.
- **Pooled training (E10):** for each target, a model trained on the other unit of the same hospital plus the same unit of the other hospital.
- **Second task (H7):** a static early-warning task reproducing a published protocol [2]: one prediction per stay at hour 12 from 12-h window summaries, for sepsis after hour 12, in stays of at least 24 h without sepsis in the first 12 h.

### Pre-registration and statistics
The study ran in documented stages. Exploration used the validation sets and seeds 0–2. Before any test-set run, the plan (versioned files) and the analysis script were frozen and committed; the test sets were then used once per experiment with seeds 100–104, fixed at project start. Inference used a patient-cluster bootstrap within each target cell (2,000 resamples; the same resampled patients for all models), averaging AUROC over seeds within each replicate; two-sided p = 2·min(P(D* ≤ 0), P(D* ≥ 0)). Holm correction was applied within each pre-registered family: {H1 LightGBM, H1 logistic regression, H2}; {H4 × 4, H5, H6 × 2}; {H7 × 4}. We logged every variant evaluated during the project (more than 300 validation evaluations) and report every pre-registered test, including those that failed.

### Comparison with published results
To check that our pipeline is comparable with published work, we re-implemented the closest published cross-hospital protocol on the same data [2] (its full text was not accessible; the protocol was taken from its abstract).

## Results

### Reproduction of published numbers
Under the published protocol our cohort comprised 30,629 stays with 1,837 sepsis events (published: 30,646 and 1,843) [2]. Gradient boosting reached AUROC 0.773 in A and 0.658 after A→B transfer, and 0.723 in B and 0.646 after B→A transfer (validation halves, single seed), compared with published XGBoost values of 0.725→0.608 and 0.702→0.636 [2]. The size of the A→B drop was almost identical (−0.115 vs −0.117); our absolute values were a few points higher, plausibly because of different predictors.

### What did not work: unlabelled fixes and density-ratio decomposition
In the diagnosis phase (validation only), a domain classifier separated the hospitals with AUC 0.9996 even after repairing encoding artefacts and 0.978 using vital signs only; importance weighting had an effective sample size of 2–5%. Overlap-based decomposition of the gap was therefore not possible, which motivated the factorial design.

### Main result: the site excess (H1)
Table 1 shows the confirmation result. Moving a model to the other hospital cost 0.071 AUROC for gradient boosting, against 0.045 for moving to the other unit of the same hospital: D = 0.026 (95% CI 0.005–0.049; Holm p = 0.018), a site-to-population ratio of 1.59. For logistic regression D = 0.063 (0.031–0.098; Holm p = 0.0015; ratio 2.21). D was positive in all four target cells for both models, and patient-level AUROC agreed (D 0.039 and 0.048). The effect was smaller than in validation (0.043 for gradient boosting).

**Table 1.** Transport gaps on the test sets (hour-level AUROC, mean of four target cells, five seeds; 95% bootstrap CI).

| Model / level | Gap, other unit same hospital | Gap, same unit other hospital | Site excess D | Holm p |
|---|---|---|---|---|
| Gradient boosting, hour | 0.045 (0.027–0.061) | 0.071 (0.053–0.090) | 0.026 (0.005–0.049) | 0.018 |
| Gradient boosting, patient | 0.048 (0.025–0.072) | 0.087 (0.062–0.110) | 0.039 (0.010–0.067) | — |
| Logistic regression, hour | 0.052 (0.027–0.077) | 0.116 (0.087–0.146) | 0.063 (0.031–0.098) | 0.0015 |
| Logistic regression, patient | 0.053 (0.025–0.079) | 0.101 (0.069–0.132) | 0.048 (0.014–0.081) | — |

### The site excess holds for other population shifts (H4)
When age band or admission route defined the within-hospital comparison, the cross-hospital loss again exceeded the within-hospital loss for both models (Table 2; all four tests Holm p ≤ 0.006). The age-band shift barely affected performance (within-hospital gap 0.004), so it is a weak control; admission route (0.026) and ICU unit (0.045) are the informative comparisons.

**Table 2.** Site excess with other within-hospital control factors (test sets).

| Control factor | Model | Within-hospital gap | Cross-hospital gap | D (95% CI) | Holm p |
|---|---|---|---|---|---|
| Age band | Gradient boosting | 0.004 | 0.062 | 0.058 (0.045–0.072) | 0.0035 |
| Age band | Logistic regression | 0.003 | 0.094 | 0.091 (0.069–0.113) | 0.0035 |
| Admission route | Gradient boosting | 0.026 | 0.050 | 0.023 (0.008–0.038) | 0.006 |
| Admission route | Logistic regression | 0.035 | 0.115 | 0.081 (0.056–0.107) | 0.0035 |

### Label-free remedies do not recover site loss (H2)
The pre-specified estimate of the share of D removed by all three label-free fixes was 0.85 (95% CI 0.26–3.13; test of a reduction, Holm p = 0.010). Decomposition shows why this number is misleading: the mean AUROC of site-transferred models did not change (0.763 without fixes, 0.762 with them), whereas within-hospital transfer fell (0.790 to 0.766) and so did the local models (0.834 to 0.813). The fixes made models worse inside their own hospital until the two gaps looked alike; they did not make models travel better. Harmonisation alone removed nothing (share −0.07, −0.62 to 0.26).

### Transported performance cannot be estimated without local labels (H3)
Label-free estimates of the transported AUROC missed by more than 0.03 in 77–80% of transfer × seed combinations for gradient boosting and 92–100% for logistic regression (n = 60 each; Table 3). Importance weighting was nearly unbiased for gradient boosting (mean error +0.003) but still had a mean absolute error of 0.067. In the split-half check, 400 labelled local patients gave an AUROC estimate within ±0.03 only 41% (gradient boosting) and 37% (logistic regression) of the time.

**Table 3.** Label-free estimation of transported AUROC (test sets).

| Model | Estimator | Mean absolute error | Mean error | Share with error > 0.03 |
|---|---|---|---|---|
| Gradient boosting | Internal AUROC | 0.072 | +0.072 | 0.80 |
| Gradient boosting | Model-implied | 0.064 | +0.045 | 0.77 |
| Gradient boosting | Importance-weighted | 0.067 | +0.003 | 0.77 |
| Logistic regression | Internal AUROC | 0.097 | +0.097 | 0.92 |
| Logistic regression | Model-implied | 0.164 | +0.164 | 1.00 |
| Logistic regression | Importance-weighted | 0.138 | −0.086 | 0.92 |

### Which features carry the site excess, size and pooling (H5, H6, E10)
Models restricted to measurement-process features showed the largest site excess (D 0.046, 0.022–0.070), whereas vital-sign-only, laboratory-only and all-but-process models showed D of 0.008–0.009 with intervals including zero. The pre-specified contrast (all features minus vital signs only) was 0.018 (−0.001 to 0.036; Holm p = 0.064) and is therefore not confirmed. With size-matched training, D remained for logistic regression (0.062, 0.030–0.095; Holm p = 0.0035); for gradient boosting the point estimate was unchanged (0.023, 0.002–0.045) but did not survive correction (Holm p = 0.064). Adding the other hospital's same-unit data to the local hospital's other-unit data improved AUROC by only 0.012 (−0.000 to 0.026).

### A second task (H7)
For the static 12-h task, all four site-excess estimates were positive (unit: 0.023 and 0.025; admission route: 0.032 and 0.054 for gradient boosting and logistic regression), but none survived correction (Holm p 0.06–0.65). Test cells contained only about 25–60 events, so this task was underpowered.

## Discussion

In two US hospital systems, a sepsis early-warning model lost more accuracy when moved to the other hospital than when moved to a different population within its own hospital. This held for three different definitions of "different population" and two model classes, with pre-registered analyses on held-out test sets. The site-specific part was not removed by unlabelled harmonisation, and the transported accuracy could not be estimated without local labels.

**What this adds.** External-validation frameworks have long aimed to separate case mix from model failure [4–6], and ML attribution methods decompose performance gaps under shift [7–9], but they rely on overlapping covariate distributions. Between these hospitals there is none. The within-hospital transfer gives an encoding-matched yardstick for population shift, so the site excess can be estimated without density ratios. The closest prior work compared within-hospital and cross-hospital shift as separate settings for conformal coverage [10], noted that unit mix confounds multi-database validation without separating the components [11], or showed that measurement-count features enlarge a cross-database drop without a population control [12]. In clinical terms, our results argue against a common hope: that a hospital can avoid local validation by choosing an external model developed on a "similar" ICU population. In our data, a model from the same hospital but a different unit was the better starting point (Tables 1 and 2), and adding external same-unit data on top helped little.

**Why remedies and estimators failed.** The site excess concentrated in models that rely on measurement-process features — information that is predictive at home because it reflects local practice, and that does not travel. Removing these features did shrink the excess, but at the price of within-hospital accuracy, so the net transported AUROC did not improve. This matches the pattern reported for MIMIC-IV→eICU mortality models with and without measurement counts [12]. Label-free estimators fail for the same reason: they assume the relation between features and outcome is stable, and the site component is precisely a change in that relation. Recent work found label-free AUROC estimators unreliable under prevalence shift in chest radiographs [13]; we find the same for multi-hospital ICU time series.

**Implications for practice.** (1) Report the factorial: when a multi-unit, multi-site dataset is available, the within-hospital transfer gives a cheap yardstick for how much of an external drop is attributable to the site. (2) Do not expect unlabelled harmonisation or label-free monitoring to substitute for local verification. (3) Budget for labelled local data: even 400 labelled patients did not reliably pin the transported AUROC to ±0.03.

**Limitations.** First, there are only two hospital systems; "site" effects here are effects of this pair, and patients, not hospitals, are the unit of inference. No other open multi-site ICU dataset with unit information exists (the open eICU demonstration subset has at most 40 stays per hospital). Second, the within-hospital controls are weaker covariate shifts than the site shift (domain-classifier AUC 0.71–0.97 within hospital vs 1.00 between); the site excess is larger than the loss from these specific population shifts, not from every conceivable one. A pre-registered dose–response analysis (validation only; Additional file 1) did not resolve this concern: across 11 within-hospital partitions the transport gap was only weakly related to the size of the covariate shift, the hospitals lay far outside the range of within-hospital shift sizes, and the cross-hospital gap was not significantly above the extrapolated within-hospital trend (residual 0.017, −0.064 to 0.060, with domain AUC as shift size). One within-hospital partition — total ICU stay of at least 48 h versus shorter, a characteristic not known at admission — produced a larger within-hospital gap (0.196) than moving between hospitals (0.069). Among partitions known at admission (unit, three age cut-offs, sex, two admission-route definitions), the cross-hospital gap was larger than every within-hospital gap; this last observation is post hoc. Third, the mechanism contrast and the second task were not confirmed, and the site excess appears task-dependent: in an exploratory, validation-only analysis of hypotension early warning across three open databases with the same unit design (Additional file 1), transport losses were small and gradient boosting showed no site excess (−0.0013, −0.0041 to 0.0013), whereas logistic regression showed a small one (0.0177, 0.0128 to 0.0221). Fourth, validation effects were consistently larger than test effects, so estimates from exploration were optimistic. Fifth, the B-hospital split had to be reconstructed after a data re-download changed the deterministic split; validation and test sets were verified to be identical to the original ones, but one training cell differed by a few patients during exploration. Sixth, gradient-boosting results varied by up to 0.018 AUROC in single validation cells between computing environments.

## Conclusions

For hourly sepsis early warning across two hospital systems, part of a model's loss in a new hospital is about the hospital itself: it exceeds the loss from moving to a different patient population within one hospital, is not removed by unlabelled harmonisation, and cannot be estimated without local labels. Hospitals adopting such models should plan for local labelled verification rather than rely on population similarity.

## Abbreviations
AUROC, area under the receiver operating characteristic curve; ICU, intensive care unit; MICU, medical ICU; SICU, surgical ICU; CI, confidence interval.

## Declarations
- **Ethics approval and consent to participate:** Secondary analysis of a public, de-identified dataset (PhysioNet/CinC 2019, CC BY 4.0). [Authors to confirm institutional requirements.]
- **Consent for publication:** Not applicable.
- **Availability of data and materials:** Data are openly available from PhysioNet. All code, pre-registered plans (versioned), frozen analysis scripts, split files, result files and the research log are available at [repository URL to be completed by the authors].
- **Competing interests:** [To be completed by the authors.]
- **Funding:** [To be completed by the authors.]
- **Authors' contributions:** [To be completed by the authors.]
- **Use of AI assistance:** The analysis code, experiments and a first draft of this manuscript were produced with an AI research assistant (Claude, Anthropic) under a documented protocol (pre-registration, frozen analyses, automated number audit). [Authors to describe their oversight and verification.]
- **Compute:** CPU only (4 cores); total about 5 machine-hours.

## References
1. Reyna MA, Josef CS, Jeter R, et al. Early prediction of sepsis from clinical data: the PhysioNet/Computing in Cardiology Challenge 2019. Crit Care Med. 2020;48:210–217. doi:10.1097/CCM.0000000000004145
2. Aaron et al. When missingness identifies the hospital: bidirectional external validation of prediction and explanation transport in sepsis AI. Preprints.org. 2026. doi:10.20944/preprints202610.1449.v1 [author list to be completed from the source]
3. Allyn J, Oliver M, Cerveau R, et al. Multi-source data integration through pooling and transfer learning improves generalizability and specialization of deep learning models for ICU mortality and length of stay prediction: a four-database external validation study. Crit Care. 2026. (PMC13353013)
4. Vergouwe Y, et al. External validity of risk models: use of benchmark values to disentangle a case-mix effect from incorrect coefficients. Am J Epidemiol. 2010. doi:10.1093/aje/kwq223
5. Debray TPA, et al. A new framework to enhance the interpretation of external validation studies of clinical prediction models. J Clin Epidemiol. 2015. doi:10.1016/j.jclinepi.2014.06.018
6. de Jong VMT, et al. Propensity-based standardization to enhance the validation and interpretation of prediction model discrimination for a target population. Stat Med. 2023. doi:10.1002/sim.9817
7. Cai TT, et al. Diagnosing model performance under distribution shift. Oper Res. 2025. doi:10.1287/opre.2023.0217
8. Zhang H, et al. "Why did the model fail?": attributing model performance changes to distribution shifts. ICML 2023. arXiv:2210.10769
9. Feng J, et al. A hierarchical decomposition for explaining ML performance discrepancies. NeurIPS 2024. arXiv:2402.14254
10. You L, et al. Missingness-aware conformal prediction under cross-hospital distribution shift. arXiv:2609.30781. 2026.
11. Rockenschaub P, et al. The impact of multi-institution datasets on the generalizability of machine learning prediction models in the ICU. Crit Care Med. 2024. doi:10.1097/CCM.0000000000006359
12. Yamamoto et al. Observation-process features are associated with larger domain shift in sepsis mortality prediction: a cross-database evaluation using MIMIC-IV and eICU. medRxiv. 2026. doi:10.64898/2026.04.05.26350209
13. Flühmann T, et al. Label-free estimation of clinically relevant performance metrics under distribution shifts. arXiv:2507.22776. 2025.
14. Garg S, et al. Leveraging unlabeled data to predict out-of-distribution performance. ICLR 2022. arXiv:2201.04234
15. Tranchellini et al. Evaluating deep learning sepsis prediction models in ICUs under distribution shift: a multi-centre retrospective cohort study. npj Digit Med. 2026. doi:10.1038/s41746-026-02364-4
16. Singh H, et al. Generalizability challenges of mortality risk prediction models: a retrospective analysis on a multi-center database. PLOS Digit Health. 2022. doi:10.1371/journal.pdig.0000023

*Reference details marked "et al." without full author lists, volumes and pages must be completed from the sources before submission.*
