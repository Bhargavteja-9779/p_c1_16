# Journal comparison (Phase 1)

Turnaround = Accepted − Received, computed by us from Crossref `assertion` metadata deposited by the publisher (script `scripts/journal_scan.py`, per-article evidence with DOIs in `journal_selection/raw/<issn>.json`). Window: articles published 2024-11-24 … 2025-11-24 (12–24 months before 2026-11-24). Up to 200 articles per journal (first Crossref page, not chosen by us).

IF = Journal Impact Factor as displayed on the publisher's official journal page (rendered text saved in `journal_selection/evidence/springer_journal_<id>.txt`, retrieved 2026-11-24). JCR quartile: **UNVERIFIED for every journal** — Clarivate JCR requires a subscription and no official page we could open displays quartile/rank.

Elsevier journals: excluded from verification — Elsevier deposits no received/accepted dates in Crossref and ScienceDirect returns HTTP 403 to this machine (decision D3). IEEE/ACM not scanned for the same reason (no date metadata in Crossref).

| ISSN | Journal | Publisher | n articles with dates | median days | IQR | range | share ≤72 d | JIF (official page) | meets ≤72 d? |
|---|---|---|---|---|---|---|---|---|---|
| 1364-8535 | Critical Care | Springer | 196 | 57.5 | 21.25–83.75 | 1–238 | 0.679 | 11.4 (2025) | yes |
| 1475-2840 | Cardiovascular Diabetology | Springer | 188 | 60.5 | 46.0–82.0 | 0–262 | 0.676 | 15.6 (2025) | yes |
| 2520-8942 | Energy Informatics | Springer | 163 | 65 | 48.0–83.0 | 26–296 | 0.626 | none shown on official page | yes |
| 2052-0492 | Journal of Intensive Care | Springer | 69 | 69 | 47.5–90.5 | 3–154 | 0.536 | 7.5 (2025) | yes |
| 1559-131X | Medical Oncology | Springer | 196 | 74.0 | 63.0–93.0 | 12–281 | 0.469 | 4.7 (2025) | no |
| 1756-8722 | Journal of Hematology & Oncology | Springer | 112 | 80.0 | 57.0–106.75 | 4–272 | 0.393 | 47.8 (2025) | no |
| 1479-5876 | Journal of Translational Medicine | Springer | 193 | 87 | 56.0–122.5 | 1–340 | 0.373 | 9.7 (2025) | no |
| 1476-4598 | Molecular Cancer | Springer | 181 | 87 | 56.0–121.0 | 17–289 | 0.409 | not checked | no |
| 1742-2094 | Journal of Neuroinflammation | Springer | 197 | 87 | 62.0–132.0 | 1–430 | 0.35 | not checked | no |
| 2050-7771 | Biomarker Research | Springer | 162 | 89.0 | 66.0–125.25 | 6–303 | 0.346 | not checked | no |
| 1756-9966 | Journal of Experimental & Clinical Cancer Research | Springer | 174 | 95.0 | 67.0–118.5 | 21–254 | 0.316 | not checked | no |
| 1573-689X | Journal of Medical Systems | Springer | 173 | 103 | 57.0–155.0 | 7–552 | 0.301 | 8.8 (2025) | no |
| 1865-0481 | Earth Science Informatics | Springer | 197 | 107 | 78.0–144.5 | 28–404 | 0.213 | not checked | no |
| 1758-9193 | Alzheimer's Research & Therapy | Springer | 193 | 107 | 81.5–155.5 | 5–610 | 0.197 | not checked | no |
| 1573-7675 | Journal of Intelligent Information Systems | Springer | 98 | 112.5 | 90.0–144.25 | 34–570 | 0.153 | not checked | no |
| 1432-1084 | European Radiology | Springer | 196 | 115.5 | 70.0–165.75 | 1–386 | 0.265 | not checked | no |
| 2523-3246 | Cybersecurity | Springer | 108 | 120.0 | 83.25–159.5 | 13–398 | 0.185 | not checked | no |
| 1475-925X | BioMedical Engineering OnLine | Springer | 147 | 124 | 86.0–187.0 | 8–544 | 0.177 | not checked | no |
| 1869-4101 | Insights into Imaging | Springer | 196 | 127.5 | 84.25–183.0 | 3–539 | 0.168 | not checked | no |
| 1758-2946 | Journal of Cheminformatics | Springer | 184 | 129.0 | 98.0–170.75 | 22–407 | 0.076 | not checked | no |
| 1748-717X | Radiation Oncology | Springer | 182 | 133.0 | 84.5–210.25 | 23–553 | 0.17 | not checked | no |
| 1435-5663 | Engineering with Computers | Springer | 142 | 138.0 | 103.25–208.25 | 34–494 | 0.07 | not checked | no |
| 2662-4443 | Communications Materials | Springer | 195 | 138 | 106.0–202.0 | 11–412 | 0.077 | not checked | no |
| 1436-3259 | Stochastic Environmental Research and Risk Assessment | Springer | 37 | 140 | 91.5–212.5 | 47–737 | 0.135 | not checked | no |
| 1471-2105 | BMC Bioinformatics | Springer | 197 | 142 | 91.0–214.0 | 38–1110 | 0.122 | not checked | no |
| 1744-8603 | Globalization and Health | Springer | 76 | 144.5 | 85.25–226.25 | 4–517 | 0.158 | not checked | no |
| 2398-6352 | npj Digital Medicine | Springer | 197 | 146 | 109.0–227.5 | 9–536 | 0.107 | not checked | no |
| 2057-3960 | npj Computational Materials | Springer | 197 | 147 | 105.0–194.5 | 10–572 | 0.086 | not checked | no |
| 2364-8228 | Applied Network Science | Springer | 68 | 149.5 | 99.25–237.75 | 40–532 | 0.132 | not checked | no |
| 2054-9369 | Military Medical Research | Elsevier BV | 73 | 150 | 113.5–244.5 | 10–730 | 0.137 | not checked | no |
| 1029-242X | Journal of Inequalities and Applications | Springer | 161 | 151 | 95.5–228.0 | 34–909 | 0.118 | not checked | no |
| 2047-2501 | Health Information Science and Systems | Springer | 82 | 153.0 | 92.75–261.25 | 42–478 | 0.098 | not checked | no |
| 2365-9440 | International Journal of Educational Technology in Higher Education | Springer | 73 | 154 | 96.5–237.5 | 29–502 | 0.082 | not checked | no |
| 1687-6180 | EURASIP Journal on Advances in Signal Processing | Springer | 65 | 154 | 97.0–242.0 | 2–428 | 0.123 | not checked | no |
| 1687-1499 | EURASIP Journal on Wireless Communications and Networking | Springer | 101 | 154 | 106.5–234.5 | 20–673 | 0.079 | not checked | no |
| 2045-2322 | Scientific Reports | Springer | 187 | 157 | 106.0–225.0 | 23–679 | 0.091 | not checked | no |
| 1743-0003 | Journal of NeuroEngineering and Rehabilitation | Springer | 196 | 161.5 | 113.0–227.0 | 7–990 | 0.056 | not checked | no |
| 1572-8145 | Journal of Intelligent Manufacturing | Springer | 198 | 170.0 | 127.0–246.25 | 48–790 | 0.045 | not checked | no |
| 1741-7015 | BMC Medicine | Springer | 198 | 176.0 | 142.0–237.0 | 21–438 | 0.03 | not checked | no |
| 2509-498X | Journal of Healthcare Informatics Research | Springer | 43 | 180 | 128.0–262.0 | 5–462 | 0.07 | not checked | no |
| 2213-7467 | Advanced Modeling and Simulation in Engineering Sciences | Springer | 39 | 182 | 114.0–261.0 | 31–614 | 0.179 | not checked | no |
| 2193-1127 | EPJ Data Science | Springer | 85 | 185 | 137.0–263.5 | 82–547 | 0.0 | not checked | no |
| 1471-2288 | BMC Medical Research Methodology | Springer | 198 | 193.0 | 114.0–359.0 | 39–698 | 0.091 | not checked | no |
| 2432-2725 | Journal of Computational Social Science | Springer | 110 | 193.5 | 142.0–231.5 | 56–630 | 0.027 | not checked | no |
| 2196-1115 | Journal of Big Data | Springer | 196 | 201.0 | 144.25–296.5 | 64–784 | 0.015 | not checked | no |
| 1573-0565 | Machine Learning | Springer | 197 | 206 | 152.5–314.5 | 19–2166 | 0.076 | not checked | no |
| 1472-6947 | BMC Medical Informatics and Decision Making | Springer | 194 | 206.5 | 116.0–377.5 | 10–837 | 0.057 | not checked | no |
| 1573-1375 | Statistics and Computing | Springer | 199 | 212 | 155.0–295.0 | 7–905 | 0.02 | not checked | no |
| 2731-3395 | Communications Engineering | Springer | 191 | 212 | 159.0–319.0 | 39–870 | 0.021 | not checked | no |
| 1366-588X | International Journal of Production Research | Taylor & Francis | 195 | 213 | 159.0–280.0 | 45–772 | 0.021 | not checked | no |
| 2196-7091 | Smart Learning Environments | Springer | 74 | 214.0 | 118.5–284.0 | 31–604 | 0.108 | not checked | no |
| 1866-9956 | Cognitive Computation | Springer | 161 | 230 | 150.5–336.5 | 36–1394 | 0.043 | not checked | no |
| 0219-3116 | Knowledge and Information Systems | Springer | 200 | 254.0 | 154.5–408.5 | 39–919 | 0.035 | not checked | no |
| 1478-7954 | Population Health Metrics | Springer | 72 | 254.0 | 151.5–424.0 | 12–2128 | 0.083 | not checked | no |
| 2662-9992 | Humanities and Social Sciences Communications | Springer | 193 | 266 | 204.0–339.0 | 90–1041 | 0.0 | not checked | no |
| 1573-1405 | International Journal of Computer Vision | Springer | 189 | 280 | 223.5–370.5 | 56–1057 | 0.005 | not checked | no |
| 1573-7462 | Artificial Intelligence Review | Springer | 21 | 281 | 169.5–346.0 | 74–383 | 0.0 | not checked | no |
| 2730-664X | Communications Medicine | Springer | 195 | 287 | 227.0–391.0 | 43–792 | 0.01 | not checked | no |
| 1573-756X | Data Mining and Knowledge Discovery | Springer | 96 | 297.0 | 174.25–437.5 | 13–990 | 0.135 | not checked | no |
| 1433-7479 | Soft Computing | Springer | 31 | 357 | 183.0–550.0 | 74–1829 | 0.0 | not checked | no |
| 2192-0567 | Energy, Sustainability and Society | Springer | 58 | 375.5 | 280.75–458.25 | 8–671 | 0.069 | not checked | no |
| 1572-9338 | Annals of Operations Research | Springer | 185 | 378 | 266.5–582.0 | 56–1225 | 0.011 | not checked | no |
| 1572-9419 | Information Systems Frontiers | Springer | 20 | 410.5 | 288.75–535.5 | 193–876 | 0.0 | not checked | no |
| 1537-274X | Journal of the American Statistical Association | Taylor & Francis | 197 | 437 | 267.5–618.0 | 3–1230 | 0.096 | not checked | no |
| 2199-4730 | Financial Innovation | Springer | 124 | 520.0 | 409.25–646.0 | 24–1099 | 0.008 | not checked | no |

## Deep check of the shortlist (all articles in window, cursor-paged; `scripts/journal_scan_deep.py`)

Letters/correspondence are accepted much faster than research papers and would bias the median downward. We therefore split by number of references deposited (≥25 refs ≈ full research article; proxy, documented as such).

| Journal | all items: n / median | full articles (≥25 refs): n / median / IQR | short items (<25 refs): n / median |
|---|---|---|---|
| Critical Care | 547 / 53 | 318 / 66.0 / 49.0–89.25 | 229 / 11 |
| Cardiovascular Diabetology | 454 / 62.0 | 443 / 62 / 46.0–86.0 | 11 / 28 |
| Energy Informatics | 163 / 65 | 102 / 64.0 / 48.0–80.25 | 61 / 67 |

Integrity screen: all shortlisted journals are Springer Nature / BMC titles (reputable publisher, not on any exclusion list we are aware of). No Web of Science delisting found for them; this screen is based on our knowledge plus the publisher pages, not on a Clarivate lookup (UNVERIFIED).

## Frontiers journals (user said on 2026-11-24 that Frontiers journals are acceptable)
Frontiers deposits no dates in Crossref. Dates were parsed from the public article pages for the first 40 Crossref DOIs in the same window (`scripts/frontiers_scan.py`, evidence in `raw/frontiers_<issn>.json`).

| Journal | n | median days | range | share ≤72 d | JIF |
|---|---|---|---|---|---|
| Frontiers in Medicine (2296-858X) | 40 | 69.5 | 1–265 | 0.525 | not checked (UNVERIFIED) |
| Frontiers in Digital Health (2673-253X) | 40 | 120 | 1–594 | 0.275 | not checked |
| Frontiers in Public Health | scan interrupted | — | — | — | — |

Conclusion: Frontiers in Medicine also passes the ≤72-day rule (on a sample of 40, letters not removed). Critical Care is kept because it passes on full articles only (n=318) and has a far higher verified JIF (11.4). Frontiers in Medicine is a second fallback.
