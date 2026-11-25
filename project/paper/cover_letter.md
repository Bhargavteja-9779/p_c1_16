[Date]

To the Editors, *Critical Care*

Dear Editors,

We submit the manuscript **"Site-specific loss of sepsis early-warning models between two hospital systems: a staged, pre-specified factorial transport analysis on open ICU data"** for consideration as a Research article.

Machine-learning early-warning models for sepsis routinely lose accuracy when moved to a new hospital, and *Critical Care* has published several external validations documenting such drops. What these studies cannot tell an adopting hospital is how much of the drop is caused by *different patients* — which choosing a model developed on a similar ICU population could fix — and how much by the *hospital itself*, which cannot be fixed that way. Standard decomposition methods need overlapping patient data between hospitals, which does not exist in practice: the two hospitals in the open PhysioNet 2019 sepsis data can be told apart from their data almost perfectly.

We address this with a simple design that needs no overlap: crossing hospital with ICU unit, so that transfer between units of the same hospital (identical data encoding) serves as a yardstick for a population shift. With staged, pre-specified analyses, frozen analysis code and held-out test sets, we find that between these two hospital systems:

1. Moving an hourly sepsis model to the other hospital cost more than moving it to a different admission-defined patient group within the same hospital (site excess 0.026 AUROC for gradient boosting, 0.063 for logistic regression). At 90% specificity, an imported model missed roughly twice as many additional septic patients as a model from the other unit of the same hospital, and its calibration deteriorated more.
2. Label-free harmonisation did not improve transported performance.
3. Label-free performance estimates missed the transported AUROC by more than 0.03 in 77–100% of transfers.

We are explicit that the effect depends on model and task: it weakened for gradient boosting when only pre-onset hours were scored, was not confirmed in a static 12-hour task, and was absent for gradient boosting in an exploratory hypotension analysis. The practical message for ICU teams is therefore modest but concrete: population similarity is not a substitute for local labelled verification. All pre-specified tests are reported, including those that failed, and the main limitation — only two hospital systems in open data with unit information — is stated plainly.

All data are open, and all code, versioned analysis plans, frozen scripts and result files will be publicly released.

This manuscript has not been published and is not under consideration elsewhere. [Competing interests and funding statements to be completed by the authors.] [Suggested reviewers, if required, to be completed by the authors.]

Sincerely,
[Corresponding author name, affiliation, contact — to be completed]
