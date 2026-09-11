# Task 25 — final experiment and independent factorial ablation

Final frozen protocol: DCASE17-T4 development set; five held-out test datasets; `alpha=.3`, `Nr=5`, `K=5`, `M=3`, `kappa=100`, one hop, no Top-P, seed 42.

Every method is constructed independently from the immutable CLAP score vector and frozen caches. No method consumes or modifies another method's result. The eight branches are iKnow, T, F, S, TF, TS, FS, and TFS.

Outputs after all datasets complete:

1. `01_final_main_results.csv`: CLAP, frozen iKnow, final TFS with Hit@1/3/5/MRR.
2. `02_ablation_hit1_mrr.csv`: complete eight-branch ablation.
3. `03_factorial_module_effects.csv`: marginal main effects of T/F/S.
4. `04_module_interactions.csv`: pairwise and three-way interactions.
5. Per-dataset `metrics.csv`, `samples.json`, `predictions.npz`, and `protocol.json`.
