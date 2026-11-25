# 2026-11-25 — RESULT: first review round and revision

The user asked for the final submission. I merged the latest parallel line (cycle 3, three-database work), wrote the manuscript and ran a simulated three-reviewer panel with fresh context. All three gave 5/10, major revision.

The reviews were fair. The most useful new evidence came from Reviewer 1's point that hour-level AUROC also rewards recognising sepsis that is already present.
- I re-scored the frozen test predictions on pre-onset hours only. This is post hoc.
- For logistic regression the site excess survives (0.059).
- For gradient boosting it shrinks to 0.019 and its CI includes 0.

So part of the gradient-boosting effect was about established sepsis. This now appears in the abstract.

Two things came out in the other direction:
- Calibration deteriorates more after site transfer than after population transfer (pre-specified secondary outcome I had not reported).
- In clinical units, an imported model misses about one in eight septic patients the local model would flag, twice the loss of a model from the other unit (post hoc).

I also corrected a reporting error the reviewer caught: I had quoted the dose–response sensitivity analysis instead of its primary. And I replaced "pre-registered" with an explicit staged timeline, because the later plans were written after earlier test results.
