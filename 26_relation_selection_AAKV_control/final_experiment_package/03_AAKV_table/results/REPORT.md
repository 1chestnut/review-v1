# Task25(g): controlled text comparison inside the full system

All three methods use the same Fusion and Selector. Only evidence text changes.

| Dataset | Direct-FS Hit@1/MRR | Raw-FS Hit@1/MRR | AAKV-TFS Hit@1/MRR |
|---|---:|---:|---:|
| ESC-50 | 93.900/95.628 | 94.100/95.765 | 94.250/95.755 |
| UrbanSound8K | 85.731/91.402 | 86.429/91.788 | 87.174/92.218 |
| FSD50K | 60.600/71.818 | 59.584/70.995 | 64.500/74.141 |
| AudioSet | 30.030/41.779 | 29.246/41.013 | 31.306/42.570 |
| TUT2017 | 47.329/65.536 | 47.991/64.845 | 56.368/70.417 |

## Paired AAKV contrasts

| Dataset | Comparison | dHit@1 [95% CI] | rescued/harmed | exact p | dMRR [95% CI] |
|---|---|---:|---:|---:|---:|
| ESC-50 | AAKV-TFS vs Direct-FS | +0.350 [-0.300,+1.000] | 25/18 | 0.3604 | +0.127 [-0.247,+0.507] |
| ESC-50 | AAKV-TFS vs Raw-FS | +0.150 [-0.500,+0.800] | 25/22 | 0.7709 | -0.010 [-0.398,+0.370] |
| UrbanSound8K | AAKV-TFS vs Direct-FS | +1.443 [+0.985,+1.913] | 280/154 | 1.524e-09 | +0.816 [+0.554,+1.085] |
| UrbanSound8K | AAKV-TFS vs Raw-FS | +0.744 [+0.286,+1.202] | 235/170 | 0.001442 | +0.429 [+0.162,+0.706] |
| FSD50K | AAKV-TFS vs Direct-FS | +3.900 [+3.196,+4.594] | 875/476 | 1.051e-27 | +2.324 [+1.886,+2.757] |
| FSD50K | AAKV-TFS vs Raw-FS | +4.916 [+4.193,+5.630] | 968/465 | 5.86e-41 | +3.146 [+2.688,+3.595] |
| AudioSet | AAKV-TFS vs Direct-FS | +1.277 [+0.812,+1.741] | 952/732 | 9.091e-08 | +0.791 [+0.482,+1.105] |
| AudioSet | AAKV-TFS vs Raw-FS | +2.060 [+1.601,+2.542] | 1043/688 | 1.363e-17 | +1.556 [+1.241,+1.871] |
| TUT2017 | AAKV-TFS vs Direct-FS | +9.038 [+7.671,+10.406] | 762/339 | 5.716e-38 | +4.881 [+4.045,+5.732] |
| TUT2017 | AAKV-TFS vs Raw-FS | +8.376 [+7.030,+9.744] | 716/324 | 1.249e-34 | +5.571 [+4.701,+6.448] |
