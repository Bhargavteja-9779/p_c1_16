# Topic candidates (cycle 1, Phase 3), written after the D9 diagnosis

Evidence base: journal entry 007 and `results/diagnosis/`. Validation data only.
Key facts:
- (F1) The gap is large: B→A 0.865 → 0.759; A→B 0.814 → 0.779.
- (F2) Pooled training recovers local performance, so the shift is learnable once target labels are available.
- (F3) Unsupervised remedies each recover ≤ 0.013 AUROC:
  - dropping process features
  - per-site quantile normalisation
  - repairing encoding artefacts
- (F4) The sites are perfectly separable (domain AUC 0.9999), and importance-weighted estimates of external AUROC miss in both directions.
- (F5) Internal validation misranked feature-set variants for external use (A→B).

| # | Candidate | Fit (Critical Care) | Prior-art risk | CPU feasible | Verdict |
|---|---|---|---|---|---|
| 1 | Missingness/measurement-process features as hospital shortcut | high | **published** (preprints202610.1449) | yes | rejected (dead end 004) |
| 2 | Label-efficient local updating of a transported sepsis model (learning curves over n local patients; recalibration vs refit vs pooled vs continued boosting) | high | **high**: WWW 2023 cross-centre sepsis for data-scarce hospitals (doi:10.1145/3543507.3583989), JBHI 2023 semi-supervised OT cross-hospital sepsis (doi:10.1109/jbhi.2023.3253208), medRxiv 2026 local retraining (doi:10.64898/2026.08.18.26360666), AJRCCM 2026 transfer vs independent training | yes | needs the closest papers opened; likely crowded |
| 3 | Evidence that cross-hospital failure is conditional shift: unsupervised remedies (normalisation, harmonisation, IW, process-feature removal) fail; label-free performance estimates are unreliable when sites are separable | medium-high | medium (DISDE / "why did the model fail" decompositions exist in general ML; not found applied to ICU sepsis) | yes | **leading**, Type C+A |
| 4 | Harmonisation audit of PhysioNet 2019 (calcium unit mixing, age encoding, EtCO2 absence, troponin assays) | medium | low (no documentation found in 3 searches) | yes | keep as a supporting finding; transport impact is small (≤ 0.01), so it cannot be the main claim |
| 5 | Internal validation misranks models for external use (accuracy-on-the-line test for ICU sepsis) | medium | medium-high (TableShift / WhyShift tabular studies) | yes | fold into #3 as a secondary analysis |
| 6 | Per-site quantile normalisation as a method | medium | medium (ComBat-style harmonisation) | yes | rejected: gain ≤ 0.013 (F3) |
| 7 | Invariant feature selection across ICU units (MICU/SICU environments) | medium | high (IRM etc.; DG rarely beats ERM on tabular data) | yes | rejected: low prior of a win |
| 8 | Seed variance / underspecification of external AUROC | medium | high (D'Amour 2020) | yes | rejected: spread ≤ 0.009 here |
| 9 | Prevalent-vs-incident sepsis composition as a driver of reported AUROC | high | medium | yes | rejected: incident drops as much as prevalent (entry 007) |
| 10 | Tabular foundation model (TabPFN-type) for few-shot local adaptation | medium | medium | marginal on CPU at 1M rows | rejected: buzzword risk, compute |
| 11 | Federated learning across the two sites | low | high | yes | rejected: crowded |
| 12 | Calibration transport (citl/slope) and local recalibration sample size | high | medium-high (Riley updating sample size; calibration drift papers) | yes | could complement #2/#3 |

Next step: open the closest papers for #2 and #3 (WWW 2023, JBHI 2023, medRxiv 2026, AJRCCM 2026, DISDE). Then decide between #3 alone and #3+#2 (diagnosis → remedy that needs labels → how many).
