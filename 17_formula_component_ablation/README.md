# Task 17 — Formula component ablation

This task freezes Task12 AAKV inputs and separates four changes that were previously bundled:

1. cardinality normalization;
2. Top-P evidence pruning;
3. two-stage base-preserving fusion;
4. dynamic versus fixed alpha.

`TwoStage-Dynamic` is required to reproduce Task12 D exactly at the per-sample rank level.

This remains an exploratory formula audit. Fixed-alpha results are not a license to choose a different alpha per test dataset.
