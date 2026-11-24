# 2026-11-24 — OBSERVATION: septic records are truncated; the process-feature asymmetry survives 3 seeds

1. Truncation (train portions only, descriptive): in both hospitals, every septic stay ends at most 9 hours after the first SepsisLabel=1 hour (median exactly 9 h; fraction ≤ 9 h = 1.00 in A and B). Since the label switches on 6 h before onset, records stop at onset + 3 h. Hour-level prevalence rises sharply with ICULOS (A: 1.6% at 0–6 h, 13.2% at >96 h; B: 1.4% → 9.3%). This explains why ICULOS alone gives AUROC ≈ 0.67–0.69 and why ICULOS dominates every model. It is a property of how the challenge data were cut, not physiology. The Applied Sciences 2026 paper (doi:10.3390/app16062735) already removes ICULOS as leakage, so this is known in part; I will not build a paper on it, but every model from now on must be evaluated with ICULOS removed or with a truncation-robust protocol.

2. Seed check (seeds 0,1,2 from SEEDS_EXPLORE; same fixed split): target-val hour AUROC
   - trained on A: full 0.763 / 0.755 / 0.763 vs no_process 0.775 / 0.776 / 0.768 → process features cost 0.005–0.021 on B.
   - trained on B: full 0.759 / 0.760 / 0.763 vs no_process 0.752 / 0.747 / 0.742 → process features add 0.007–0.021 on A.
   - process_only: A→B 0.691 / 0.695 / 0.705; B→A 0.758 / 0.751 / 0.743.
   The sign of the process-feature effect on transfer flips with direction in all three seeds. Seeds only vary the learner; the split is fixed, so this is not yet evidence across resamples of patients.

Prior art on the asymmetry: the "When Missingness Identifies the Hospital" preprint reports observation indicators carrying 24.7% (A→B) vs 7.5% (B→A) of external SHAP mass, and that removing them changed external AUROC by < 0.01. So the asymmetry has been glimpsed at the attribution level but not explained, and their pooled ablation hides the sign flip I see.
