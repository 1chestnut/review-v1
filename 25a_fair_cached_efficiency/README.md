# Task 25(a) - Fair cached efficiency comparison

## Question

How much **online inference cost** does the final one-hop TFS method add relative to frozen iKnow, under the same CLAP model, data, hardware and reasonable offline caches?

This is not a second-hop experiment. `TFS-All47` is not used as the principal efficiency baseline. The three methods are `CLAP`, `Frozen-iKnow`, and `Final-TFS (alpha=.3, Nr=5)`.

## Offline work excluded from online latency

KG entity mapping, RotatE Top-M retrieval, deterministic evidence verbalization, AAKV generation, and all category/evidence text embeddings are computed once and cached. Their storage footprint is reported. AAKV generation is an offline preprocessing cost and is never hidden inside per-audio latency.

## Online work included

- **CLAP:** live audio loading/preprocessing/encoding, category matching and ranking.
- **Frozen-iKnow:** CLAP plus Top-K selection, audio-to-direct-evidence matching, joint NormLSE and ranking.
- **Final-TFS:** CLAP plus per-relation AAKV evidence matching, Consensus-Margin relation selection, retain Nr=5, hierarchical fusion and ranking.

Two clocks are reported: end-to-end latency from the audio path, and knowledge-stage latency starting from the current audio embedding. This prevents CLAP audio encoding from concealing the added cost of knowledge reasoning.

## Fairness controls

All methods for a given dataset run sequentially on the same isolated GPU, with the same 200 evenly spaced samples, identical sample order and immutable caches. Different datasets may run concurrently on three separate GPUs; the physical GPU identity is recorded and no cross-GPU latency comparison is used to claim a method advantage. Both batch sizes 1 and 32 are measured after a 20-sample warm-up. Every setting is repeated five times; method order is rotated and CUDA is synchronized. Top-1 agreement across live re-encoding repeats must be at least 99.5%. Complete ranking hashes are retained for audit but are not required to be identical because numerically near-tied, low-ranked classes can exchange order without changing the evaluated prediction.

Task25 full-dataset metrics supply Hit@1/MRR. The timing subset is used only for profiling, never for headline accuracy.

## Outputs

- Per dataset: `timing_repeats.csv`, `timing_summary.csv`, `protocol.json`.
- Global: `01_efficiency_complete.csv`.
- Global: `02_performance_efficiency_tradeoff.csv`, including delta MRR per added millisecond relative to frozen iKnow.
