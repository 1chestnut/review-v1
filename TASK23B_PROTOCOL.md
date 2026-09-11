# Task 23B — five-test-set parameter landscape (diagnostic only)

This task repeats the exact Task23 six-cell grid on ESC-50, UrbanSound8K, FSD50K, AudioSet, and TUT2017. It is an exploratory diagnostic of cross-dataset parameter preference, not a parameter-selection protocol.

- Complete TFS is enabled in every cell.
- Only `alpha in {0.3,0.5,0.7}` and `Nr in {1,3}` vary.
- One hop, `K=5`, `M=3`, `Top-P=All`, `kappa=100`, and seed 42 remain fixed.
- The five datasets remain test sets. Their labels must not be used to choose dataset-specific settings or revise the frozen DCASE-selected configuration.
- The valid final configuration remains the one selected on DCASE in Task23. These tables may only be reported as post-hoc sensitivity/robustness analysis.
