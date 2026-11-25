[Date]

To the Editors, *Critical Care*

Dear Editors,

We submit the manuscript **"How much of a sepsis early-warning model's failure in a new hospital is about the hospital? A pre-registered factorial transport analysis on open multi-site ICU data"** for consideration as a Research article.

Machine-learning early-warning models for sepsis routinely lose accuracy when moved to a new hospital, and *Critical Care* has published several external validations documenting such drops. What these studies cannot tell an adopting hospital is how much of the drop is caused by *different patients* — which choosing a model developed on a similar ICU population could fix — and how much by the *hospital itself*, which cannot be fixed that way. Standard decomposition methods need overlapping patient data between hospitals, which does not exist in practice: the two hospitals in the open PhysioNet 2019 sepsis data can be told apart from their data almost perfectly.

We address this with a simple design that needs no overlap: crossing hospital with ICU unit, so that transfer between units of the same hospital (identical data encoding) serves as a yardstick for a population shift. Using pre-registered hypotheses, frozen analysis code and held-out test sets, we find that:

1. Moving an hourly sepsis model to the other hospital costs more than moving it to a different population within the same hospital (site excess 0.026 AUROC for gradient boosting, 0.063 for logistic regression), and this holds for three different definitions of "different population".
2. Label-free harmonisation does not make models travel better; it only makes them worse at home.
3. Label-free performance estimates miss the transported AUROC by more than 0.03 in 77–100% of transfers, and even 400 labelled local patients do not reliably pin it down.

The practical message for ICU teams is that population similarity is not a substitute for local labelled verification. We report every pre-specified test, including those that failed (a mechanism contrast and replication in a second, underpowered task), and state the main limitation plainly: only two hospital systems are available in open data with unit information.

All data are open, and all code, versioned analysis plans, frozen scripts and result files will be publicly released.

This manuscript has not been published and is not under consideration elsewhere. [Competing interests and funding statements to be completed by the authors.] [Suggested reviewers, if required, to be completed by the authors.]

Sincerely,
[Corresponding author name, affiliation, contact — to be completed]
