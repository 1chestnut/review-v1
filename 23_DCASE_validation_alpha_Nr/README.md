# Task 23 — DCASE validation of alpha and relation count

DCASE17-T4 (419 samples) is designated as the development/validation set and must be removed from the final test table and test-set macro average.

The complete TFS method is enabled in every grid cell: frozen AAKV verbalization, hierarchical normalized-LSE fusion, and label-free Consensus-Margin relation selection. Only `alpha` and `Nr` change.

## Fixed configuration

- One hop; `K=5`; `M=3`; `Top-P=All` (disabled); `kappa=100`; seed 42.
- Frozen CLAP, RotatE, strict entity mapping, AAKV JSON, relation pool, dataset order, and evaluation code.
- DCASE labels are never used by the per-sample selector. They are consulted only after inference to calculate validation-set metrics.

## Grid and selection rule

- `alpha in {0.3, 0.5, 0.7}`.
- `Nr in {1, 3}`.
- Select the highest validation MRR.
- Configurations within 0.1 percentage points of the best MRR are treated as tied; prefer `Nr=1`, then `alpha` closest to 0.5.
- After selection, freeze the configuration and evaluate it once on the other five datasets without further adjustment.
