# Task 23C — expanded DCASE validation grid

The complete TFS method is fixed. Only `alpha` and the retained relation-expert count `Nr` vary.

- `alpha in {0.3, 0.5, 0.7}`.
- Eligible `Nr in {1, 3, 5, 10}`.
- `Nr=47 (All)` is a no-selection control and is excluded from hyperparameter selection.
- Fixed: one hop, `K=5`, `M=3`, no Top-P, `kappa=100`, seed 42, frozen AAKV, strict mapping, CLAP, RotatE, relation pool, and Consensus-Margin ranking.
- Selection rule fixed before reading this expanded grid: maximize DCASE Hit@1; exact Hit@1 ties maximize MRR; remaining ties prefer smaller `Nr`.
- DCASE labels are used only to calculate aggregate validation metrics. They never enter per-sample relation routing.
- Once selected, the configuration must be frozen for the other five test datasets.
