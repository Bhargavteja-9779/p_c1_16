# Reported results — ML prediction models in *Critical Care* (2023–2026)

Every number below was taken from the full text of the article (Europe PMC `fullTextXML`, saved as `literature/raw/<PMCID>.xml`). Numbers in supplements we did not retrieve are labelled as such. "Not reported" means the main text does not give it. All 17 DOIs (15 original papers and 2 reviews) resolve through doi.org (HTTP 302). Status: all 17 VERIFIED. Per-paper fields (datasets, n, sites, split, models, baselines, missing-data handling, code) are in `journal_papers_matrix.csv`.

Extraction was done by a delegated sub-agent. The lead agent spot-checked 7 numbers against the raw XML (Allyn 0.897/0.773, Lim 0.964/0.870, Chiang 0.82, Guan 0.769, Koumantakis 0.55); all were present.

## C1. Internal → external performance changes actually reported

| Paper (PMCID) | Internal | External | Source in paper |
|---|---|---|---|
| Allyn 2026, TPC, ICU mortality (PMC13353013) | MIMIC-IV-trained 0.897; HiRID 0.851; eICU 0.788; AmsterdamUMC 0.774 | 0.773 (−13.8%); 0.777 (−8.7%); 0.768 (−2.5%); 0.808 (+4.4%) | Table 2 |
| Allyn 2026 | AUPRC change by training source | −3.3% to −40.8% | Table 2 |
| Allyn 2026, generalization to unseen eICU + HiRID | AUROC: AmsterdamUMC-only 0.78; MIMIC-only 0.80 | pooling 0.82 | Table 3 |
| Lim 2024, iMORS 24-h mortality (PMC10938661) | 0.964 | MIMIC-III 0.890; eICU 0.886; AmsterdamUMC 0.870 | Results / Fig. 1 |
| Lim 2024, ECE | 0.146 | 0.205 / 0.199 / 0.254 | Add. file Fig. E8 |
| Chiang 2025, TvHEWS (PMC12285179) | AUROC 0.93; AUPRC 0.82; Brier 0.082 | temporal 0.92 / 0.79 / 0.085; MIMIC-IV 0.82 / 0.61 / 0.116 | Fig. 3, Fig. 4 |
| Zappalà 2024, persistent AKI 3 (PMC11149298) | auROC 90.42 (AmsterdamUMC), 92.63 (MIMIC-III) | eICU 93.58; MargheritaTre 85.29 | Table 2 (intervals given as IQR) |
| Guan C. 2024, new-onset AF (PMC11523862) | 0.891 | 0.769 (same hospital, earlier era) | Results / Fig. 3 |
| Jonkers 2026, distributional AKI (PMC13162413) | 0.948 (temporal MIMIC-IV) | 0.984 UZGent; 0.969 eICU; 0.988 AmsterdamUMC | Table 2 |
| Gross 2025, Shock-Net, ED (PMC12257722) | 0.959 | 0.937 | Methods |
| Oh 2025, ORAKLE (PMC12105202) | 0.84 (XGBoost 0.81; Cox 0.80) | SICdb 0.83 / eICU 0.85 (XGBoost 0.80/0.83; Cox 0.79/0.81) | Results / Fig. 4 |
| He R. 2026, pediatric sepsis (PMC13776461) | NICU 0.846; PICU 0.803 (18-feature model) | NICU 0.742 / 0.827; PICU 0.717 / 0.811 | Results / Fig. 2 / Table 2 |
| Yu H. 2025, HFNC (PMC11887196) | RNFCV 0.87 (LOOCV 0.93) | 0.79 | Table 2 |
| Koumantakis 2025, readmission review (PMC12535055) | Lim 0.82; Moazemi 0.80 | Lim 0.77 / 0.73; Moazemi 0.55 | Results |
| Bomrah 2024, sepsis scoping review (PMC11131234) | Lin: sensitivity 0.80, specificity 0.78 | 0.67 / 0.70 | Table 3 |

Papers where no internal→external AUROC comparison can be made from the main text:
- Natarajan 2026 (PMC12947465): no external validation. Hospitalization-level AUROC was 0.83 for LGBM vs 0.74 for SIRS on Emory/PhysioNet 2019, and 0.72 vs 0.68 on MIMIC-IV (Appendix Table 6 / Table 1).
- Blythe 2024 (PMC11256441): internal–external CV only. Mean held-out-hospital Uno AUC was 0.97 at 12 h.
- Guan C. 2023 (PMC10598960): only held-out-hospital AUCs (RF 0.9378, XGBoost 0.9492).
- Huang 2023 (PMC10327364): regression. External MAE 18.1 ml/min vs 20.6 for the reference.
- Venkatesh 2025 (PMC12326670): no external validation (AUROC 82.3).

Patterns in these numbers (descriptive only):
1. The largest drops came from training on a single, distinctive source: MIMIC-IV-trained −13.8% (Allyn), 0.891 → 0.769 (Guan 2024), NICU 0.846 → 0.742 (He).
2. One model can lose performance at one external site and keep it at another (Zappalà eICU vs MargheritaTre; He external 1 vs external 2).
3. Where both metrics were reported, AUPRC fell more than AUROC (Allyn; Chiang).

## C2. Missing-data handling (15 original papers)
- **Forward fill as the core strategy (6 papers):**
  - Allyn: with missingness masks.
  - Natarajan: remaining NaN left to LightGBM.
  - Lim: median imputation for the first value, plus time-since-last-measurement features.
  - Chiang: within variable-specific windows, no imputation.
  - Zappalà: with absence indicators and recency features.
  - Oh: followed by zero-fill and then MICE.
- **Explicit missingness indicators:** only Allyn and Zappalà. Lim used time-delta features only.
- **Model-based imputation:** missRanger (Blythe), KNN (Guan 2024), multiple imputation (Guan 2023), mean/mode (Huang). Venkatesh used complete cases after MICE "provided little to no benefit".
- **Not described:** Jonkers, Gross, Yu, and He (beyond excluding variables >5% missing).
- **Cross-site missingness:** Allyn describes missingness as MNAR and institution-dependent. Zappalà used MargheritaTre to test robustness to high missingness.
- **No paper tested** whether measurement-process features help or harm cross-site transport.

## C3. Open data, code, compute
- 10/15 papers use at least one open or credentialed ICU database; 5 use only open data; 5 use only private data.
- Code on GitHub: 4/15 (Allyn, Blythe, Guan 2023, Jonkers).
- Compute is essentially never reported.

## C4. Calibration under external validation
- 6/15 papers report external, temporal or held-out-site calibration (Lim, Chiang, Jonkers, Oh, Yu (supplement), Blythe).
- Where reported, calibration usually got worse externally: Lim ECE 0.146 → 0.199–0.254; Chiang Brier 0.082 → 0.116. It held in Oh (Brier 0.21 throughout) and Jonkers (ECE ≤ 0.008).
- 7/15 papers report no calibration statistic.

## C5. Uncertainty and seeds
- Only He R. states a fixed seed. **No paper reports variance across training seeds.**
- Several papers have internal inconsistencies between the abstract and the body: Guan 2024 CI; Venkatesh 82.7 vs 0.829 vs 0.827; Zappalà IQR vs 95% CI; Koumantakis 0.78 vs 0.79.

## Relevance to our study
The journal's recent ML papers keep showing an internal→external gap, and none of them separates *where the gap comes from*. Candidate sources are case-mix, measurement practice, label prevalence, and calibration. None reports seed variance or measurement-process ablations. This is the evidence base for the topic choice in `topic/`.
