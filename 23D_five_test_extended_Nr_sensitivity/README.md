# Task 23D — cross-dataset sensitivity after validation freeze

The DCASE validation result from Task23C is frozen as `alpha=0.3, Nr=5`. This task does not select or revise parameters.

It computes the missing `Nr={5,10,47}` cells for each of the five test datasets at `alpha={0.3,0.5,0.7}`. These cells are merged with Task23B's existing `Nr={1,3}` cells and Task23C's DCASE grid to provide a complete six-dataset sensitivity analysis.

- `Nr=47` denotes the all-relations/no-selection control.
- All other settings are identical to Task23C.
- Test labels are used only for post-hoc reporting of sensitivity curves, never for configuration selection.
- The final test configuration remains `alpha=0.3, Nr=5` regardless of which post-hoc cell is numerically best on an individual test dataset.
