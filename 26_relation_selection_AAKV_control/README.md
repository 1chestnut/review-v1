# Task26: controlled relation-selection comparison under AAKV

This task starts automatically only after Task25(g) has completed and finalized.

## Question

With AAKV text, frozen hierarchical NormLSE fusion, and the same KG evidence,
does sample-level label-free relation selection outperform non-adaptive choices?

## Methods

- `AAKV-FrozenRq`: the frozen dataset-specific relation set used by the iKnow reproduction.
- `AAKV-Frequency5`: five relations with the most cached class-tail evidence items; static and label-free.
- `AAKV-Random5-s42/s43/s44`: five randomly sampled relations per audio with three fixed seeds.
- `AAKV-Selector5`: sample-level Consensus-Margin selection of five relations.

Frozen for every branch: samples, CLAP, KG, strict entity mapping, K=5, M=3,
one hop, AAKV text, alpha=0.3, Nr=5 where applicable, no Top-P, normalized-LSE
hierarchical fusion, deterministic audio seed, and evaluation protocol.

Ground-truth labels are used only after inference to compute metrics. They are
never used for relation selection. Complete per-sample ranks and selected
relations are saved for paired statistics.
