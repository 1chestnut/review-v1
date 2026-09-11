# Task 21 results — no Top-P

All results use one-hop knowledge, `K=5`, `M=3`, `R=1`, `kappa=100`, fixed `alpha=0.5`, seed 42, and no Top-P pruning. Deltas are percentage points relative to `I_Frozen-iKnow-05b`.

| Dataset | T dH1 / dMRR | F dH1 / dMRR | S dH1 / dMRR | TF dH1 / dMRR | TS dH1 / dMRR | FS dH1 / dMRR | TFS dH1 / dMRR |
|---|---:|---:|---:|---:|---:|---:|---:|
| ESC-50 | -3.10 / -1.94 | +1.80 / +0.93 | +2.10 / +1.06 | +2.05 / +1.14 | +1.10 / +0.39 | +2.20 / +1.12 | **+2.50 / +1.33** |
| UrbanSound8K | -0.37 / -0.49 | +0.24 / +0.15 | +0.95 / +0.27 | +1.27 / +0.66 | **+2.07 / +0.49** | +0.39 / +0.09 | +1.72 / **+0.75** |
| FSD50K | +1.76 / +0.84 | +1.36 / +0.90 | +0.46 / +0.10 | +3.18 / +1.90 | **+4.54 / +2.24** | -0.02 / -0.57 | +4.24 / +2.02 |
| DCASE17-T4 | -1.43 / -0.91 | +0.48 / +0.51 | **+1.91 / +1.49** | +1.67 / +1.26 | +1.67 / +0.71 | -1.43 / -0.93 | +1.19 / +0.43 |
| AudioSet | -0.56 / -0.38 | +0.64 / +0.47 | +0.66 / +0.18 | +0.75 / +0.53 | **+1.91 / +0.86** | +0.65 / -0.06 | +1.79 / +0.76 |
| TUT2017 | +5.71 / +2.62 | +2.61 / +1.51 | +2.74 / +0.95 | +7.09 / +3.78 | +9.19 / +4.31 | +1.24 / +0.01 | **+9.47 / +4.57** |
| Macro mean | +0.33 / -0.04 | +1.19 / +0.75 | +1.47 / +0.67 | +2.67 / +1.54 | +3.41 / +1.50 | +0.50 / -0.06 | **+3.49 / +1.64** |

Legend: T = AAKV verbalization; F = hierarchical fixed-alpha fusion; S = label-free `Consensus-Margin-Top1` relation selector.

## Conclusions

1. F and S are independently robust: both improve Hit@1 and MRR over frozen iKnow on all six datasets.
2. T alone is not robust (only two of six datasets improve), so AAKV should not be claimed as an independently universal improvement.
3. T becomes useful conditionally: both TF and TS improve over iKnow on all six datasets.
4. TFS has the strongest macro result (+3.49 Hit@1, +1.64 MRR) and improves over iKnow on all six datasets, but it is not the per-dataset optimum everywhere.
5. FS has an adverse interaction without AAKV; it is not a stable recommended configuration.
6. These are exploratory single-run effect estimates. Statistical claims require paired bootstrap confidence intervals and McNemar tests on the saved per-sample predictions.
