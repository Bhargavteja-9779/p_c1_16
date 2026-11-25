# 2026-11-24 — DIAGNOSIS: where does the A↔B drop come from? (D9, validation only, seed 0)

What I ran: `python -m src.diagnose --seed 0` — LightGBM, fixed hyperparameters (decision D12), early stopping on source-val, 6 feature sets × 2 directions. Results: `results/diagnosis/diag_lgb_*_s0.json`; log of variants in `state/variants_tried.csv` (24 rows = 12 models × 2 evaluation sets). Total fit time ≈ 74 s.

Hour-level AUROC, source-val → target-val (patient-level AUROC in the JSON files):

| feature set | trained on A (A-val → B-val) | trained on B (B-val → A-val) |
|---|---|---|
| full | 0.814 → 0.763 | 0.862 → 0.759 |
| no_process | 0.787 → 0.775 | 0.844 → 0.752 |
| no_iculos | 0.796 → 0.738 | 0.851 → 0.726 |
| no_process_no_iculos | 0.751 → 0.728 | 0.824 → 0.693 |
| process_only (+ICULOS) | 0.805 → 0.691 | 0.805 → 0.758 |
| iculos_only | 0.699 → 0.669 | 0.687 → 0.693 |

What I see:
1. Both directions lose 0.05–0.10 AUROC on transfer with every feature set. Hour-level AUPRC roughly halves (A full 0.117 → 0.057).
2. **The measurement-process effect is asymmetric.** Trained on A, process features raise internal AUROC (+0.027) and lower transfer AUROC (−0.012 vs no_process); a process-only model collapses A→B (0.805 → 0.691). Trained on B, process features help in both hospitals (+0.007 on A) and a process-only model transports well (0.805 → 0.758). So "measurement patterns are a hospital shortcut" (the published finding, journal entry 004) is true for one direction only and depends on which variables carry the signal: in A the top process features are FiO2/Lactate timing; in B they are PaCO2/EtCO2 timing.
3. ICULOS (time in ICU) is the top feature in every model with it, and removing it costs 0.025–0.06 target AUROC. ICULOS alone already gives 0.67–0.69. This is a known artefact risk of the 2019 challenge label (labels are only defined during the stay; septic stays are truncated) — it must be treated as a possible leak, not a strength.
4. HospAdmTime (hours from hospital to ICU admission) is a top-3 feature in almost every model. It is plausibly administrative/site-specific rather than physiological.

Caveats: one seed, no tuning, early stopping on log-loss stopped at 36–139 trees; differences of ~0.01 are within what I would expect from seed noise. Nothing here is a result; it is a map of where to look.
