# 2026-11-24 — DEAD END (as a primary claim): "missingness patterns are hospital shortcuts"

My first idea for a topic was: in ICU data, *whether and when* a lab is measured reflects local practice, so models that lean on measurement patterns should score well internally and fail in another hospital; PhysioNet 2019 (hospital systems A and B) would show it.

Before building anything I searched for it. It is already done, very recently and on exactly this data:
- "When Missingness Identifies the Hospital: Bidirectional External Validation of Prediction and Explanation Transport in Sepsis AI" (Preprints.org, Oct 2026, doi:10.20944/preprints202610.1449.v1). Abstract (read): elastic-net/RF/XGBoost trained in A or B, tested in the other; XGBoost AUROC fell from 0.725 internally to 0.608 after transfer; includes an ablation without observation indicators and hospital-identification classifiers.
- Related method work: "Domain Generalization under Sampling Pattern Shifts in Irregular Time Series" (arXiv 2609.33279, PRISM), "Missingness-Aware Conformal Prediction Under Cross-Hospital Distribution Shift" (arXiv 2609.30781), "Robust prediction under missingness shifts" (arXiv 2406.16484), "Domain Adaptation under Missingness Shift" (arXiv 2211.02093), Agniel et al. BMJ 2018 (lab-ordering process bias).

So an audit of the same phenomenon would add nothing. I keep the observation (it is a real, independently reported transfer failure: 0.725 → 0.608) as motivation, and look for an angle these papers leave open.
