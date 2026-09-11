# Tasks 23C/23D sensitivity summary

## Post-hoc numerical preferences

| Dataset | Highest-MRR grid cell | MRR | Hit@1-first observation |
|---|---|---:|---|
| DCASE validation | alpha=.3, Nr=5 | 75.688 | alpha=.3 ties for best Hit@1 across Nr=1/3/5/10; MRR selects Nr=5 |
| ESC-50 | alpha=.5, Nr=1 | 95.905 | alpha=.3 and .5 tie for best Hit@1 |
| UrbanSound8K | alpha=.3, Nr=10 | 92.229 | alpha=.3 gives best Hit@1 |
| FSD50K | alpha=.3, Nr=10 | 74.202 | alpha=.3 gives best Hit@1 |
| AudioSet | alpha=.5, Nr=10 | 42.620 | alpha=.3, Nr=3 gives best Hit@1 |
| TUT2017 | alpha=.3, Nr=10 | 70.460 | alpha=.3, Nr=10 gives best Hit@1 |

The test-set preferences above are sensitivity diagnostics only and are not used for configuration selection.

## Frozen DCASE-selected configuration versus iKnow

The formal configuration is `alpha=.3, Nr=5`.

| Test dataset | iKnow H1 | Final H1 | dH1 | iKnow MRR | Final MRR | dMRR |
|---|---:|---:|---:|---:|---:|---:|
| ESC-50 | 91.750 | 94.250 | +2.500 | 94.572 | 95.755 | +1.183 |
| UrbanSound8K | 84.883 | 87.174 | +2.290 | 91.078 | 92.218 | +1.140 |
| FSD50K | 59.838 | 64.500 | +4.662 | 71.802 | 74.141 | +2.340 |
| AudioSet | 29.217 | 31.306 | +2.089 | 41.538 | 42.570 | +1.032 |
| TUT2017 | 43.697 | 56.368 | +12.671 | 63.711 | 70.417 | +6.706 |

## Interpretation

- `alpha=.3` is the most stable Hit@1 setting across datasets.
- Increasing `Nr` generally changes MRR/Hit@3 more than Hit@1; many Hit@1 curves plateau.
- `Nr=47` generally degrades Hit@1/MRR, supporting selective rather than exhaustive relation use.
- The DCASE-selected `alpha=.3, Nr=5` outperforms frozen iKnow in Hit@1 and MRR on all five test datasets.
- Dataset-specific numerical optima must not replace the frozen validation-selected configuration.
