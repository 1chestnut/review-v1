# Consolidated controlled ablation (Task25 + Task25g)

Task25 supplies the independent 2^3 ablation of AAKV, Fusion and Selector. Task25g adds RawTriple under the identical Fusion+Selector branch.

Protocol check passed for every dataset: identical samples, K=5, M=3, alpha=0.3, one hop, Top-P disabled, seed=42, CLAP/KG/mapping and evaluation protocol.

| Dataset | Frozen iKnow | AAKV only | Fusion only | Selector only | AAKV+Fusion | AAKV+Selector | Fusion+Selector Direct | Fusion+Selector Raw | Full AAKV+Fusion+Selector |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ESC-50 | 91.75/94.57 | 88.65/92.63 | 92.85/95.15 | 93.85/95.63 | 92.70/95.09 | 92.85/94.90 | 93.90/95.63 | 94.10/95.76 | 94.25/95.75 |
| UrbanSound8K | 84.88/91.08 | 84.52/90.59 | 85.02/91.18 | 85.83/91.44 | 85.78/91.47 | 86.96/91.86 | 85.73/91.40 | 86.43/91.79 | 87.17/92.22 |
| FSD50K | 59.84/71.80 | 61.60/72.65 | 60.83/72.49 | 60.29/71.88 | 62.71/73.47 | 64.38/73.92 | 60.60/71.82 | 59.58/70.99 | 64.50/74.14 |
| AudioSet | 29.22/41.54 | 28.65/41.16 | 29.64/41.88 | 29.87/41.77 | 29.75/41.88 | 31.13/42.40 | 30.03/41.78 | 29.25/41.01 | 31.31/42.57 |
| TUT2017 | 43.70/63.71 | 49.40/66.33 | 46.35/65.44 | 46.43/65.25 | 51.28/67.86 | 52.91/68.25 | 47.33/65.54 | 47.99/64.85 | 56.37/70.42 |

Each cell reports Hit@1/MRR. The factorial table should be used for module ablation; Raw-FS is an additional verbalization control, not a ninth factorial branch.

## Primary clean contrasts

| Dataset | Fusion (F−I) H1/MRR | AAKV in full context (TFS−FS) | Selector in full context (TFS−TF) | Full−iKnow |
|---|---:|---:|---:|---:|
| ESC-50 | +1.10/+0.57 | +0.35/+0.13 | +1.55/+0.67 | +2.50/+1.18 |
| UrbanSound8K | +0.14/+0.10 | +1.44/+0.82 | +1.40/+0.75 | +2.29/+1.14 |
| FSD50K | +1.00/+0.69 | +3.90/+2.32 | +1.79/+0.67 | +4.66/+2.34 |
| AudioSet | +0.42/+0.34 | +1.28/+0.79 | +1.56/+0.69 | +2.09/+1.03 |
| TUT2017 | +2.65/+1.73 | +9.04/+4.88 | +5.09/+2.55 | +12.67/+6.71 |
