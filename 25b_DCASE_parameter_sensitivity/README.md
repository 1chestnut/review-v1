# Task 25(b) - DCASE development-set parameter sensitivity

## Role and boundary

This folder is the frozen sensitivity-analysis snapshot used by the final Task25 protocol. DCASE17-T4 is the **development/validation dataset**. It is excluded from the five-dataset final test table.

Only DCASE is included here because `alpha` and `Nr` were selected with DCASE labels. The five test datasets must not be used to select or revise these parameters. Task23D remains an internal post-hoc diagnostic and is deliberately not copied into this formal parameter-selection folder.

## Grid and fixed variables

- `alpha = {0.3, 0.5, 0.7}`
- `Nr = {1, 3, 5, 10, 47}`
- `Nr=47` is an all-relations/no-selection diagnostic and is ineligible for selection.
- Fixed: one hop, `K=5`, `M=3`, `kappa=100`, Top-P disabled, AAKV frozen, seed 42.

The complete TFS method is held fixed while only `alpha` and `Nr` vary. The predeclared rule maximizes Hit@1; exact Hit@1 ties maximize MRR; remaining ties prefer smaller `Nr`. The selected configuration is `alpha=0.3, Nr=5`.

## Files

- `validation_grid_hit1_first.csv`: formal grid reported in the manuscript.
- `selected_config_hit1_first.json`: frozen decision and selection rule.
- `metrics.json`, `samples.json`, `protocol.json`: full audit trail.
- `source/`: exact source code and original README from Task23C.
