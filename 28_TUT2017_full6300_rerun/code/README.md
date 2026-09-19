# Task 28: TUT2017 complete 6,300-clip rerun

This task preserves all previous 4,680-clip results and reruns TUT2017 with the
official development (4,680) and evaluation (1,620) partitions combined, matching
the 6,300 clips reported by iKnow. The method configuration remains unchanged:
K=5, M=3, kappa=100, alpha=0.3, Nr=5, seed=42, identical entity mapping, RotatE,
AAKV dictionary, relation pool, fusion, and selector.

Outputs are separated into `main`, `raw`, `selector`, and `statistics`. No old
result is overwritten until the 6,300-sample audit and all reruns pass.
