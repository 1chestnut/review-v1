# Task 14 completed results

All six datasets completed successfully. `1st-P5` exactly matches Task 12 method
D at the per-sample rank level.

## Task 14A: second-edge wording only

All paths, M2=1, shared P=5, gamma=0.85, scoring and audio embeddings are fixed.

| Dataset | Fallback Hit@1 | AAKV Hit@1 | Delta Hit@1 | Fallback MRR | AAKV MRR | Delta MRR |
|---|---:|---:|---:|---:|---:|---:|
| ESC-50 | 93.6500 | 93.6000 | -0.0500 | 95.6297 | 95.5980 | -0.0317 |
| UrbanSound8K | 85.8910 | 85.9711 | +0.0802 | 91.5559 | 91.5993 | +0.0433 |
| FSD50K | 62.7211 | 62.8678 | +0.1466 | 73.4576 | 73.5654 | +0.1078 |
| DCASE17-T4 | 62.2912 | 62.0525 | -0.2387 | 74.7131 | 74.5501 | -0.1631 |
| AudioSet | 29.9774 | 29.9542 | -0.0232 | 42.1216 | 42.0748 | -0.0468 |
| TUT2017 | 49.3803 | 49.3590 | -0.0214 | 66.6522 | 66.6543 | +0.0021 |

AAKV wording alone is not a general explanation for second-hop value. FSD50K is
the only clear wording improvement in paired MRR confidence intervals.

## Task 14B: best exploratory fixed M2/P effect versus matched one-hop P

The row below selects the largest MRR difference only for diagnosis; it is not a
valid final hyperparameter selection on test data.

| Dataset | Diagnostic best grid cell | Delta Hit@1 (pp) | Delta MRR (pp) |
|---|---|---:|---:|
| ESC-50 | M1/P3 | 0.0000 | -0.0292 |
| UrbanSound8K | M5/P5 | +0.0573 | -0.0359 |
| FSD50K | M1/P10 | +0.1955 | +0.0704 |
| DCASE17-T4 | M3/P3 | -0.2387 | -0.5171 |
| AudioSet | M3/P3 | +0.1683 | +0.1223 |
| TUT2017 | M1/P10 | -0.2137 | -0.1043 |

No common M2/P cell gives a positive macro-average MRR effect. AudioSet M3/P3
has a paired MRR 95% CI of [0.0294, 0.2209] pp; the remaining fixed gains are
small or negative after matching the one-hop evidence budget.

## Pure second-hop sample-oracle potential at fixed P

Each oracle chooses among the matched one-hop method and M2={1,3,5} at the same
P. It uses ground truth only after inference and is analysis-only.

| Dataset | Largest fixed-P Oracle Delta Hit@1 (pp) | Largest fixed-P Oracle Delta MRR (pp) |
|---|---:|---:|
| ESC-50 | +0.1000 | +0.0583 |
| UrbanSound8K | +0.6757 | +0.4795 |
| FSD50K | +0.9188 | +0.6161 |
| DCASE17-T4 | +1.1933 | +0.8671 |
| AudioSet | +1.0909 | +0.8843 |
| TUT2017 | +0.3205 | +0.2671 |

This shows meaningful sample-level complementarity on UrbanSound8K, FSD50K,
DCASE17-T4 and AudioSet, but little headroom on ESC-50 and modest headroom on
TUT2017. The evidence supports testing an unlabeled selector/gate; it does not
support claiming that full second-hop expansion is generally beneficial.

## AAKV generation and entity audit

| Dataset | Valid intermediate KG entities | Generated paths | Universal fallback rate |
|---|---:|---:|---:|
| ESC-50 | 487/487 | 10,679 | 2.6% |
| UrbanSound8K | 151/151 | 4,371 | 12.8% |
| FSD50K | 958/958 | 16,915 | 2.9% |
| DCASE17-T4 | 175/175 | 4,764 | 11.4% |
| AudioSet | 2,179/2,179 | 38,977 | 2.0% |
| TUT2017 | 133/133 | 2,998 | 21.5% |

Intermediate-entity lookup is not the cause of the weak fixed results. The high
fallback rate on TUT2017 and, to a lesser extent, UrbanSound8K/DCASE should be
considered when interpreting wording effects.

## Current conclusion

Increasing M2/P and replacing the second-edge fallback with AAKV do not by
themselves make full second-hop expansion consistently useful. The oracle gap
shows that selected samples can benefit, so the next bounded experiment should
freeze one common M2/P configuration and compare full versus an unlabeled gate.
Simple CLAP-margin tertiles are not uniformly beneficial across datasets, so a
claim based only on the old delta=0.02 margin rule would currently be weak.
