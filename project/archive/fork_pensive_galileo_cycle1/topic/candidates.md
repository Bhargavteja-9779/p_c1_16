# Topic candidates (cycle 1, Phase 3) — written after the D9 diagnosis (journal 006, 007)

Scoring: F = fit to Critical Care, N = distance from closest prior work found so far, T = tractable on 4 CPUs within 15 h, D = public data. 1–5 each.

| # | Candidate | Closest prior work found | F | N | T | D | Verdict |
|---|---|---|---|---|---|---|---|
| 1 | Missingness patterns are a hospital shortcut (A↔B) | Preprint 10.20944/preprints202610.1449.v1 | 4 | 1 | 5 | 5 | REJECT — published (journal 004) |
| 2 | ICULOS / record-truncation shortcut in PhysioNet 2019 | Applied Sciences 10.3390/app16062735 removes ICULOS; JMIR 10.2196/72083 evaluation strategies | 3 | 2 | 5 | 5 | REJECT as main claim; adopt as protocol requirement |
| 3 | **Which measurement-process signals transport, and why** — per-variable decomposition of the direction-dependent effect of process features; test a mechanism (clinician-triggered vs protocol-driven measurement) | Preprint above (attribution asymmetry, no explanation); medRxiv 10.64898/2026.04.05.2635020 (process features ↔ larger shift, mortality, MIMIC/eICU); medRxiv 10.64898/2026.03.17.26348414 (care-process intensity falsification) | 5 | 3 | 5 | 4 | **SELECT (tentative)** — must pass deeper prior-art check |
| 4 | How much local data is needed to update a transported sepsis model (learning curves for recalibration / revision / refit / continued boosting) | medRxiv 10.64898/2026.08.18.26360666 (local retraining); Critical Care 2026 pooling+transfer (10.1186/s13054-026-06…); Research Square local recalibration ICU deterioration | 5 | 2 | 5 | 5 | Backup; crowded |
| 5 | Selective use of process features: keep only those whose measurement policy is stable across sites (target-unlabelled criterion) | Missingness-shift robustness (arXiv 2406.16484, 2211.02093), PRISM (arXiv 2609.33279) | 4 | 3 | 5 | 5 | Fold into #3 as the method arm |
| 6 | Missingness-aware conformal alerts across hospitals | arXiv 2609.30781 | 4 | 1 | 5 | 5 | REJECT — done |
| 7 | Federated / pooled training A+B | Applied Sciences 2026; many FL papers | 3 | 1 | 4 | 5 | REJECT — crowded |
| 8 | Transformer / foundation model for sepsis | SepsisFlow arXiv 2611.13661 etc. | 2 | 1 | 1 | 5 | REJECT — buzzword, GPU |
| 9 | Explanation (SHAP) stability under transfer | Same preprint (Jaccard top-10) | 3 | 1 | 5 | 5 | REJECT — done |
| 10 | Fixed alert-rate evaluation across hospitals | Applied Sciences 2026 | 4 | 1 | 5 | 5 | REJECT — done |
| 11 | Label-definition sensitivity (Sepsis-3 variants) | JAMA Netw Open 2026 (10.1001/jamanetworkopen.2026.5599) | 4 | 2 | 2 | 2 | REJECT — needs MIMIC (credentialed) |
| 12 | Case-control vs cohort sampling bias in sepsis prediction | Nat Commun 2021 temporal bias; medRxiv 2025 case-control matching | 3 | 1 | 5 | 5 | REJECT — done |

Second dataset for breadth (needed for G7): eICU-CRD demo (2.0.1, ODbL; ~2.5k stays, 20 hospitals) supports multi-hospital process-feature analysis but has no sepsis label; PhysioNet 2012 (4 ICU types, mortality). Plan: use 2012 (ICU type as "site") and eICU demo (hospital as site) for a mortality task to test whether the mechanism found on 2019 generalises.
