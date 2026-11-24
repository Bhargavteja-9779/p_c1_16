# 2026-11-24 — OBSERVATION: almost no Q1 journal accepts in ≤72 days

I measured Accepted − Received myself from Crossref metadata for 65 journals (Springer Nature, BMC, Taylor & Francis). Only 4 have a median ≤ 72 days: Critical Care (57.5 d on 196 items), Cardiovascular Diabetology (60.5), Energy Informatics (65), Journal of Intensive Care (69). Most ML/CS journals sit at 150–400 days (e.g. Machine Learning 206, Data Mining and Knowledge Discovery 297).

I then worried that Critical Care's speed comes from letters. It partly does: short items (<25 references) have a median of 11 days. But full research articles still have a median of 66 days (n=318). So it passes, with less margin than the headline number suggested. Evidence: journal_selection/raw/deep_1364-8535.json.

This decides the domain: intensive-care medicine. The study must be clinically meaningful and use open ICU data, because credentialed datasets (MIMIC, eICU full) are not something I can obtain autonomously.
