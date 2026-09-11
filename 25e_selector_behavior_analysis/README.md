# Task 25(e) - Selector behavior analysis

This is a post-hoc, CPU-only analysis of the frozen Task25 per-sample outputs. It does not rerun CLAP, regenerate evidence, tune parameters, or alter predictions.

It tests whether Consensus-Margin behaves as a genuinely sample-dependent relation selector rather than collapsing to one fixed relation set. It reports relation frequency, top-relation entropy, number of unique selected relation sets, dominant-set share, overlap with the frozen iKnow relation set, performance by consensus-vote strength, and relation diversity within the same ground-truth class.

Ground truth is used only after inference to summarize correctness and within-class behavior. It is never used by the selector. Relation-conditioned performance is descriptive rather than causal because selected relations co-occur.

Outputs:

- `01_dataset_selector_summary.csv`
- `02_relation_frequency.csv`
- `03_performance_by_consensus_votes.csv`
- `04_descriptive_effect_when_relation_selected.csv`
- `05_within_class_relation_diversity.csv`
- `REPORT.md` and `protocol.json`
