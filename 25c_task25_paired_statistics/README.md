# Task 25(c) - Paired statistical analysis of Task25

This task reads the independently generated, per-sample ranks from Task25. It does not rerun CLAP and does not use DCASE.

The primary confirmatory comparison is Final-TFS versus Frozen-iKnow on each of the five held-out test datasets. It reports paired Bootstrap 95% confidence intervals for delta Hit@1 and delta MRR, exact two-sided McNemar tests for Hit@1, Holm correction across the five tests, and wrong-to-correct versus correct-to-wrong transitions.

Secondary module contrasts measure T, F and S individually against iKnow and measure the incremental addition of each module to the other two. They are explicitly exploratory and receive a separate Holm correction across all 30 comparisons.

The system is frozen and deterministic, so changing random seeds does not constitute independent model training. Statistical uncertainty is estimated over paired test samples.
