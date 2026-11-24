# 2026-11-24 — RESULT: E6 confirmation (test set, seeds 100–104, frozen analysis at 641c403)

All 100 confirmation jobs finished. I ran the frozen scripts unchanged (`analyze_transport.py --nboot 2000`, `e5_estimators.py`). Files: results/analysis/E6_confirm_test.json, tables/E6_confirm_test_transport.md, tables/E5_E6_confirm_test.md, logs/analyze_E6.log, logs/e5_E6.log.

**H1 (site gap > unit gap): supported for both model classes.**
- LightGBM, hour level: gap_unit 0.045 [0.027, 0.061], gap_site 0.071 [0.053, 0.090], D = 0.026 [0.005, 0.049]; bootstrap p 0.018, Holm p 0.018; site/unit ratio 1.59.
- Logistic regression: D = 0.063 [0.031, 0.098]; p 0.0005, Holm p 0.0015; ratio 2.21.
- Patient level agrees: LightGBM D 0.039 [0.010, 0.067]; LR D 0.048 [0.014, 0.081].
- D was positive in all 4 target cells for both models.
- The effect is smaller than in validation (LightGBM D 0.043 in E1). Validation was optimistic.

**H2 (share of the site component removed by unlabelled fixes): the pre-specified number is misleading.**
- The pre-specified estimate is 0.85 [0.26, 3.13] for harm+noproc+norm, and the Holm test "reduction > 0" gives p 0.010.
- But the mean AUROC by source role shows how D shrinks. Site-source AUROC does not move: 0.763 → 0.762. Unit-source AUROC falls (0.790 → 0.766), and so does the local model (0.834 → 0.813). These are means of the 3-decimal per-cell values in the log.
- So the fixes do not make a model transfer better to another hospital. They make it worse inside its own hospital until the two gaps look alike.
- Harmonisation alone removes nothing (share −0.07 [−0.62, 0.26]).
- This does not contradict the frozen test, but the "share removed" framing would be dishonest without this decomposition. It is now the main H2 message: unlabelled fixes do not recover site loss.

**H3 (label-free AUROC estimates miss by > 0.03 in most transfers): supported.**
- Share of transfer × seed with |error| > 0.03 (n = 60 per row): LightGBM internal 0.80, implied 0.77, IW 0.77; LR 0.92, 1.00, 0.92.
- IW is almost unbiased for LightGBM (mean error +0.003) but still has MAE 0.067.
- Few-label check (split-half): even 400 local patients give a ±0.03 AUROC estimate only 41% (LightGBM) or 37% (LR) of the time.
- Domain classifiers separate every pair of cells (AUC 0.90–1.0), so overlap-based estimators have no support.

Garden-of-forking-paths count: 265 variant rows logged before E6, which was a single frozen run. Caveat from journal 011: the B_MICU training set in E1/E2 exploration differed slightly from the one E6 used.
