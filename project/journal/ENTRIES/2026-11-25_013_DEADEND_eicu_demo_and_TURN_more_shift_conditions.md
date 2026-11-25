# 2026-11-25 — DEAD END (eICU demo) and TURN: more shift conditions inside PhysioNet 2019

The user asked me to improvise more. The weakest parts are breadth (one dataset, one control factor) and mechanism (I can say the site costs more, not why).

I first checked whether the open eICU-CRD demo could host the same factorial. It cannot. It has 2,520 stays from 186 hospitals, at most 40 per hospital, and about 220 deaths in total. Most hospital × unit cells would have fewer than five events. The full eICU, MIMIC-IV, HiRID and AmsterdamUMCdb all need credentialed access, which I do not have here.

So I am widening the design inside PhysioNet 2019, where the factorial logic still works. The unit was just one possible "same hospital, different patients" control. If the site excess is real, it should also appear when the control is age band (< 65 vs ≥ 65) or admission route (ICU within 24 h of hospital admission vs later). I fixed both definitions before looking at any outcome.

Then a mechanism question. Prediction, written down now: the site excess lives in the labs and measurement-process features (charting practice), and shrinks for vitals-only models.

I also added a size-matched check, because the B cells are larger than the A cells, and a practical question. Does adding the other hospital's same-unit data to your own hospital's other-unit data help?

All of this goes on validation first; the analysis is frozen before any test run (plan_v3.yaml).
