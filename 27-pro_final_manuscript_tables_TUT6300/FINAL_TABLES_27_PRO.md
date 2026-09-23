# 27-pro: final manuscript tables with complete TUT2017 (6,300 clips)

This directory is independent of `27_final_manuscript_tables`; the original summary is unchanged.
TUT2017 now combines the official development (4,680) and evaluation (1,620) partitions.

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
| TUT2017 | CLAP | 40.65 | 76.59 | 92.24 | 60.79 |
| TUT2017 | I_iKnow | 44.14 | 79.89 | 92.68 | 64.04 |
| TUT2017 | TFS_Final | 56.87 | 80.54 | 91.79 | 70.73 |

## Table 2. Factorial ablation (Hit@1 / MRR, %)

| Dataset | iKnow | AAKV | Fusion | Selector | AAKV+Fusion | AAKV+Selector | Fusion+Selector | Full |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ESC-50 | 91.75/94.57 | 88.65/92.63 | 92.85/95.15 | 93.85/95.63 | 92.70/95.09 | 92.85/94.90 | 93.90/95.63 | 94.25/95.75 |
| UrbanSound8K | 84.88/91.08 | 84.52/90.59 | 85.02/91.18 | 85.83/91.44 | 85.78/91.47 | 86.96/91.86 | 85.73/91.40 | 87.17/92.22 |
| FSD50K | 59.84/71.80 | 61.60/72.65 | 60.83/72.49 | 60.29/71.88 | 62.71/73.47 | 64.38/73.92 | 60.60/71.82 | 64.50/74.14 |
| AudioSet | 29.22/41.54 | 28.65/41.16 | 29.64/41.88 | 29.87/41.77 | 29.75/41.88 | 31.13/42.40 | 30.03/41.78 | 31.31/42.57 |
| TUT2017 | 44.14/64.04 | 48.68/66.20 | 46.86/65.86 | 46.56/65.39 | 51.29/67.99 | 53.54/68.80 | 47.87/65.93 | 56.87/70.73 |
| MacroMean | 61.97/72.61 | 62.42/72.65 | 63.04/73.31 | 63.28/73.22 | 64.44/73.98 | 65.77/74.38 | 63.63/73.31 | 66.82/75.08 |

## Table 3. AAKV verbalization, Panel B (same Fusion+Selector system)

| Dataset | Direct-FS | Raw-FS | AAKV-TFS |
|---|---:|---:|---:|
| ESC-50 | 93.90/95.63 | 94.10/95.76 | 94.25/95.75 |
| UrbanSound8K | 85.73/91.40 | 86.43/91.79 | 87.17/92.22 |
| FSD50K | 60.60/71.82 | 59.58/70.99 | 64.50/74.14 |
| AudioSet | 30.03/41.78 | 29.25/41.01 | 31.31/42.57 |
| TUT2017 | 47.87/65.93 | 47.95/64.97 | 56.87/70.73 |

## Table 4. Relation-selection comparison (Hit@1 / MRR, %)

| Dataset | FrozenRq | Frequency5 | Random5 mean | Selector5 |
|---|---:|---:|---:|---:|
| ESC-50 | 92.70/95.09 | 92.85/95.23 | 92.45/94.90 | 94.25/95.75 |
| UrbanSound8K | 85.78/91.47 | 85.10/91.04 | 86.02/91.61 | 87.17/92.22 |
| FSD50K | 62.48/73.32 | 62.60/73.26 | 63.26/73.62 | 64.50/74.14 |
| AudioSet | 29.62/41.81 | 29.92/42.03 | 29.82/41.92 | 31.31/42.57 |
| TUT2017 | 51.29/67.99 | 50.54/67.40 | 52.10/68.54 | 56.87/70.73 |

## Appendix C. Sample-adaptive relation selection behavior

| Dataset | #Samples | #Unique Top-5 sets | Dominant-set share (%) | Mean Jaccard vs FrozenRq |
|---|---:|---:|---:|---:|
| ESC-50 | 2,000 | 1,708 | 1.40 | 0.0405 |
| UrbanSound8K | 8,732 | 5,461 | 1.53 | 0.0739 |
| FSD50K | 10,231 | 9,066 | 1.51 | 0.0549 |
| AudioSet | 17,233 | 15,671 | 1.50 | 0.0577 |
| TUT2017 | **6,300** | 4,336 | 1.06 | 0.0636 |

The unique-set and dominant-set statistics ignore relation order. Mean Jaccard uses each dataset's complete FrozenRq set (four to six relations); the selector always retains five. The corresponding 47-relation frequencies for all five datasets are in `AppendixC_relation_frequency.csv`. The TUT2017 row is from the final 6,300-clip Task 28 selector records, not Task 25e.

## TUT2017 old-to-new audit

| Method | old Hit@1 | new Hit@1 | delta | old MRR | new MRR | delta |
|---|---:|---:|---:|---:|---:|---:|
| CLAP | 40.49 | 40.65 | +0.16 | 60.25 | 60.79 | +0.54 |
| I_iKnow | 43.70 | 44.14 | +0.45 | 63.71 | 64.04 | +0.33 |
| TFS_Final | 56.37 | 56.87 | +0.51 | 70.42 | 70.73 | +0.31 |

## Integrity note

- Tables 1, 2, 3 Panel B, 4, 6 and 7 use the complete 6,300-clip TUT2017 rerun.
- Table 3 Panel A in the CSV is retained only as a legacy auxiliary result. Its TUT2017 row still uses 4,680 clips and must not be cited as a complete-data result unless those four branches are rerun.
- Table 5 is unchanged because the development protocol and frozen parameters did not change.
