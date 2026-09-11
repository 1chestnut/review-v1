# Final manuscript experiment tables

All reported final-test values use the five test datasets. DCASE17-T4 is used only for development and parameter selection.

## Table 1. Main results (%)

| Dataset | Method | Hit@1 | Hit@3 | Hit@5 | MRR |
|---|---|---:|---:|---:|---:|
| ESC-50 | CLAP | 91.10 | 96.75 | 97.65 | 94.11 |
| ESC-50 | I_iKnow | 91.75 | 97.05 | 97.65 | 94.57 |
| ESC-50 | TFS_Final | 94.25 | 96.80 | 97.65 | 95.75 |
| UrbanSound8K | CLAP | 83.76 | 96.60 | 98.65 | 90.40 |
| UrbanSound8K | I_iKnow | 84.88 | 96.77 | 98.65 | 91.08 |
| UrbanSound8K | TFS_Final | 87.17 | 96.90 | 98.65 | 92.22 |
| FSD50K | CLAP | 57.35 | 79.65 | 86.35 | 70.17 |
| FSD50K | I_iKnow | 59.84 | 80.73 | 86.51 | 71.80 |
| FSD50K | TFS_Final | 64.50 | 80.58 | 86.46 | 74.14 |
| AudioSet | CLAP | 28.65 | 46.36 | 54.80 | 41.06 |
| AudioSet | I_iKnow | 29.22 | 47.04 | 54.87 | 41.54 |
| AudioSet | TFS_Final | 31.31 | 46.93 | 54.86 | 42.57 |
| TUT2017 | CLAP | 40.49 | 75.02 | 91.67 | 60.25 |
| TUT2017 | I_iKnow | 43.70 | 79.55 | 92.12 | 63.71 |
| TUT2017 | TFS_Final | 56.37 | 80.41 | 91.54 | 70.42 |

## Table 2. Factorial ablation (Hit@1 / MRR, %)

| Dataset | iKnow | AAKV | Fusion | Selector | AAKV+Fusion | AAKV+Selector | Fusion+Selector | Full |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ESC-50 | 91.75/94.57 | 88.65/92.63 | 92.85/95.15 | 93.85/95.63 | 92.70/95.09 | 92.85/94.90 | 93.90/95.63 | 94.25/95.75 |
| UrbanSound8K | 84.88/91.08 | 84.52/90.59 | 85.02/91.18 | 85.83/91.44 | 85.78/91.47 | 86.96/91.86 | 85.73/91.40 | 87.17/92.22 |
| FSD50K | 59.84/71.80 | 61.60/72.65 | 60.83/72.49 | 60.29/71.88 | 62.71/73.47 | 64.38/73.92 | 60.60/71.82 | 64.50/74.14 |
| AudioSet | 29.22/41.54 | 28.65/41.16 | 29.64/41.88 | 29.87/41.77 | 29.75/41.88 | 31.13/42.40 | 30.03/41.78 | 31.31/42.57 |
| TUT2017 | 43.70/63.71 | 49.40/66.33 | 46.35/65.44 | 46.43/65.25 | 51.28/67.86 | 52.91/68.25 | 47.33/65.54 | 56.37/70.42 |
| MacroMean | 61.88/72.54 | 62.56/72.67 | 62.94/73.23 | 63.26/73.20 | 64.44/73.95 | 65.65/74.27 | 63.52/73.23 | 66.72/75.02 |

## Table 3. AAKV verbalization analysis (Hit@1 / MRR, %)

### Panel A. Fixed iKnow aggregation and fixed relations

| Dataset | Direct | RawTriple | General LLM | AAKV |
|---|---:|---:|---:|---:|
| ESC-50 | 91.75/94.57 | 89.50/93.41 | 88.00/92.34 | 88.65/92.63 |
| UrbanSound8K | 84.65/90.96 | 84.32/90.64 | 80.90/88.80 | 84.31/90.51 |
| FSD50K | 59.47/71.50 | 57.19/70.19 | 60.24/71.87 | 61.32/72.45 |
| AudioSet | 29.14/41.41 | 27.38/40.16 | 28.21/40.85 | 28.36/41.02 |
| TUT2017 | 43.63/63.86 | 47.91/65.69 | 41.07/60.85 | 48.97/66.25 |

### Panel B. Same Fusion+Selector system

| Dataset | Direct-FS | Raw-FS | AAKV-TFS |
|---|---:|---:|---:|
| ESC-50 | 93.90/95.63 | 94.10/95.76 | 94.25/95.75 |
| UrbanSound8K | 85.73/91.40 | 86.43/91.79 | 87.17/92.22 |
| FSD50K | 60.60/71.82 | 59.58/70.99 | 64.50/74.14 |
| AudioSet | 30.03/41.78 | 29.25/41.01 | 31.31/42.57 |
| TUT2017 | 47.33/65.54 | 47.99/64.85 | 56.37/70.42 |

## Table 4. Relation-selection comparison (Hit@1 / MRR, %)

| Dataset | FrozenRq | Frequency5 | Random5 mean | Selector5 |
|---|---:|---:|---:|---:|
| ESC-50 | 92.70/95.09 | 92.85/95.23 | 92.45/94.90 | 94.25/95.75 |
| UrbanSound8K | 85.78/91.47 | 85.10/91.04 | 86.02/91.61 | 87.17/92.22 |
| FSD50K | 62.48/73.32 | 62.60/73.26 | 63.26/73.62 | 64.50/74.14 |
| AudioSet | 29.62/41.81 | 29.92/42.03 | 29.82/41.92 | 31.31/42.57 |
| TUT2017 | 51.28/67.86 | 50.09/67.00 | 51.76/68.24 | 56.37/70.42 |

## Table 5. Parameters and frozen protocol

| Parameter | Value | Role | Source/selection | Test status |
|---|---|---|---|---|
| Development dataset | DCASE17-T4, 419 available samples | Select method-level hyperparameters only | Declared development set; excluded from the five final test datasets | not reported as test result |
| K | 5 | CLAP top candidate classes receiving KG enrichment | Inherited and frozen from the iKnow reproduction | fixed |
| M | 3 | RotatE tail entities retained per (head, relation) | Inherited and frozen from the iKnow reproduction | fixed |
| kappa | 100 | Normalized log-sum-exp similarity scale | Aligned with the frozen CLAP/iKnow reproduction score scale | fixed |
| alpha | 0.3 | Base CLAP weight; knowledge weight is 1-alpha | Selected once on DCASE development set by MRR | fixed on all five tests |
| N_r | 5 | Relations retained by the sample-level selector | Selected jointly with alpha on DCASE development set | fixed on all five tests |
| Candidate relation pool | 47 RotatE relations | Relations available to the selector | Complete frozen KG relation vocabulary; not selected using test labels | fixed |
| Top-P | All (disabled) | No additional evidence-score pruning | Removed after controlled analysis showed no necessary contribution | fixed |
| Hop | 1 | One-hop KG enrichment | Second-hop branch removed from the final method | fixed |
| Knowledge text | AAKV | Constrained audio-aware KG verbalization | Generated offline with fixed prompt, verification and recorded fallback protocol | frozen before inference |
| Seed | 42 + SHA256(audio path) | Deterministic per-sample execution | Same sample seed for every compared branch | fixed |
| Primary metrics | Hit@1, Hit@3, Hit@5, MRR | Ranking evaluation; highest-ranked positive used for multi-label samples | One common evaluator for all methods | fixed |
