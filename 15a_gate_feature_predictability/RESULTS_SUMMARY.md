# Task 15A results — can a pre-second-hop gate predict benefit?

The analysis completed without new CLAP or KG inference. Ground truth was used
only after inference to define diagnostic benefit/harm labels.

## Benefit prevalence

| Dataset | N | Any M2 at P5 improves rank | Fixed M1/P5 improves | Fixed M1/P5 worsens |
|---|---:|---:|---:|---:|
| ESC-50 | 2,000 | 2 | 1 | 4 |
| UrbanSound8K | 8,732 | 133 | 50 | 89 |
| FSD50K | 10,231 | 153 | 78 | 119 |
| DCASE17-T4 | 419 | 12 | 5 | 14 |
| AudioSet | 17,233 | 461 | 239 | 405 |
| TUT2017 | 4,680 | 19 | 5 | 45 |

Beneficial second-hop samples are sparse (0.1%–2.86%), and the fixed M1/P5
configuration harms more samples than it improves on every dataset.

## Best single pre-second-hop feature for detecting any P5 benefit

| Dataset | Feature | AUROC | AUPRC | Benefit prevalence |
|---|---|---:|---:|---:|
| ESC-50 | negative first-hop margin | 0.997* | 0.571* | 0.10% |
| UrbanSound8K | base/first JS divergence | 0.879 | 0.205 | 1.52% |
| FSD50K | first-hop entropy | 0.731 | 0.048 | 1.50% |
| DCASE17-T4 | weak evidence support | 0.763 | 0.064 | 2.86% |
| AudioSet | first-hop entropy | 0.636 | 0.043 | 2.68% |
| TUT2017 | weak evidence support | 0.748 | 0.012 | 0.41% |

*ESC-50 has only two positive samples, so its apparently high AUROC is unstable
and must not be treated as strong evidence.

## Leave-one-dataset-out transfer

The lightweight logistic analysis was trained on five datasets and evaluated on
one held-out dataset. AUROC was 0.981*, 0.793, 0.696, 0.700, 0.591 and 0.681 for
ESC-50, UrbanSound8K, FSD50K, DCASE17-T4, AudioSet and TUT2017, respectively.
AUPRC remained low because useful samples are rare. At a 20% trigger budget, the
router still selected more fixed-M1/P5 harmful than beneficial samples on every
dataset.

## Conclusion

The old single margin threshold is not adequate. Several pre-second-hop features
contain predictive signal, especially JS divergence, first-hop entropy and weak
evidence support, but the current fixed M1/P5 second-hop update is too often
harmful for the exploratory router to yield a reliable general gain. This result
supports a two-part next step only if second hop is retained: (1) predict both
benefit and harm/abstention, not benefit alone; and (2) evaluate on a declared
development-to-test protocol. It does not yet support claiming a successful
dynamic gate.
