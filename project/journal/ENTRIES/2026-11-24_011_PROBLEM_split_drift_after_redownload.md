# 2026-11-24 — PROBLEM: the hospital-B split drifted after re-downloading the data

Another container swap. When I relaunched E6, the first jobs crashed: the processed caches are git-ignored and had not been rebuilt. I wrote `scripts/prepare_data.py` to rebuild them.

Before trusting the rebuilt data I re-ran one finished E6 job and compared it to the stored predictions. Hospital A matched exactly. Hospital B did not: the B test cells had different patients (B_MICU 1,410 vs 1,400). The file contents for shared patients were identical. What changed was the split. The split rule is deterministic, but its shuffle depends on the full patient table, and the previous session's B table was slightly different. Its download log ends with `bad=27`. Today's download has 0 malformed files out of 40,336.

Accepting the new split would have put patients I had looked at during exploration (old train/val) into the B test set. So I rebuilt the old assignment from the prediction files already in git. Every val and test set now matches the old ones bit for bit, and three of four checked jobs reproduce with zero prediction difference. The exception is B_MICU training: the old B_MICU training set must have differed by a few patients. Its single-seed validation AUROCs move by up to 0.011, which is about seed-noise size. I pinned the split in git (`configs/splits_v1.csv`) so this cannot happen again.

Limitation to carry into the paper: E1/E2 exploration models trained on B_MICU used a slightly different (defective) training set from the one E6 uses.
