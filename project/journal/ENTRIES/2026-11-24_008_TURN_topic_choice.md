# 2026-11-24 — TURN: from "how to adapt" to "what kind of shift, and what that rules out"

Given entry 007, my natural next idea was a learning curve for local model updating. Opening the closest papers changed my mind. An npj Digital Medicine 2026 multi-centre study already compares fine-tuning, retraining, target training, supervised DA and fusion training across target-data sizes, and two 2023 papers do semi-supervised cross-hospital sepsis transfer. None of them shows *what kind* of shift causes the failure, or what that implies for unlabelled fixes and label-free performance estimates.

So the draft topic is now: show that the shift is conditional; show the consequences (unsupervised remedies close little of the gap, and label-free estimates mislead); then ask how few labelled local patients are enough to verify a model before deployment. Before building the estimator I still have to check prediction-powered inference, which may already cover it.
