# Task 13 completed summary

## Frozen comparison

`D-1st` exactly reproduces Task 12 method D. `D-2nd-Controlled` changes only the
availability of filtered second-hop candidates. Both methods use K=5, M1=3,
dynamic alpha, AAKV first-hop texts and one shared final Top-P=5 evidence budget.
The exploratory second hop uses M2=1, gamma=0.85 and no selective gate.

| Dataset | D-1st Hit@1 | D-2nd Hit@1 | Delta Hit@1 (pp) | D-1st MRR | D-2nd MRR | Delta MRR (pp) | MRR paired bootstrap 95% CI |
|---|---:|---:|---:|---:|---:|---:|---|
| ESC-50 | 93.7000 | 93.6500 | -0.0500 | 95.6605 | 95.6297 | -0.0308 | [-0.1225, 0.0525] |
| UrbanSound8K | 86.0513 | 85.8910 | -0.1603 | 91.6756 | 91.5559 | -0.1197 | [-0.2016, -0.0384] |
| FSD50K | 62.7700 | 62.7505 | -0.0195 | 73.5634 | 73.4731 | -0.0903 | [-0.1888, 0.0049] |
| DCASE17-T4 | 63.2458 | 62.2912 | -0.9547 | 75.3575 | 74.7131 | -0.6444 | [-1.4122, 0.0636] |
| AudioSet | 29.9193 | 30.0006 | +0.0812 | 42.0540 | 42.1377 | +0.0837 | [0.0113, 0.1572] |
| TUT2017 | 49.6368 | 49.3803 | -0.2564 | 66.8398 | 66.6522 | -0.1877 | [-0.2771, -0.1129] |

## Entity-chain audit

Every first-hop tail used here was found in the original KG entity vocabulary and
could be passed directly as a second-hop head:

| Dataset | Valid second-hop heads / first-hop tails |
|---|---:|
| ESC-50 | 487 / 487 |
| UrbanSound8K | 151 / 151 |
| FSD50K | 958 / 958 |
| DCASE17-T4 | 175 / 175 |
| AudioSet | 2,179 / 2,179 |
| TUT2017 | 133 / 133 |

Thus, the present lack of gain is not explained by losing intermediate entities
during display-text remapping. Empty class-level second-hop evidence can still
occur after self-loop, return-to-origin and duplicate filtering.

## Interpretation boundary

Under this exploratory M2=1, gamma=0.85, total-P=5 configuration, controlled
second-hop expansion does not provide a general gain: five datasets do not
improve and only AudioSet has a small positive MRR change. This does not yet prove
that every possible second-hop method is useless. In particular, the second-hop
text in this run uses Task 10's deterministic verified universal fallback rather
than newly generated Qwen sentences, and M2/gamma/P were not development-selected.
It does show that simply adding valid, filtered second-hop candidates is not
sufficient to support the proposed contribution.
