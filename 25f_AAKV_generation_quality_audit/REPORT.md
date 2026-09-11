# Task25(f): AAKV generation-quality and interaction audit

## Automatic generation audit

| Dataset | triples | first pass | repaired | fallback | head kept | tail kept | exact prefix | duplicate texts | median words |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| ESC-50 | 487 | 90.55% | 8.62% | 0.82% | 100.00% | 99.38% | 100.00% | 0 | 9.0 |
| UrbanSound8K | 151 | 85.43% | 8.61% | 5.96% | 100.00% | 99.34% | 100.00% | 0 | 9.0 |
| FSD50K | 958 | 94.26% | 4.70% | 1.04% | 100.00% | 100.00% | 100.00% | 1 | 8.0 |
| DCASE17-T4 | 175 | 74.86% | 6.86% | 18.29% | 100.00% | 99.43% | 100.00% | 0 | 10.0 |
| AudioSet | 2179 | 93.90% | 4.64% | 1.47% | 100.00% | 99.86% | 100.00% | 0 | 10.0 |
| TUT2017 | 133 | 65.41% | 10.53% | 24.06% | 100.00% | 100.00% | 100.00% | 0 | 9.0 |

## Interaction interpretation

Effects are paired within the same audio samples. Positive interaction means the joint effect exceeds additive component effects; a CI crossing zero is only a trend.

| Dataset | contrast | dHit@1 [95% CI] | dMRR [95% CI] |
|---|---|---:|---:|
| ESC-50 | AAKV_main_effect_alone_T_minus_I | -3.100 [-4.350, -1.850] | -1.938 [-2.671, -1.224] |
| ESC-50 | AAKV_added_to_Selector_TS_minus_S | -1.000 [-1.850, -0.200] | -0.733 [-1.236, -0.242] |
| ESC-50 | AAKV_added_to_FusionSelector_TFS_minus_FS | +0.350 [-0.300, +1.000] | +0.127 [-0.246, +0.501] |
| ESC-50 | AAKV_x_Selector_interaction_TS-T-S+I | +2.100 [+0.900, +3.300] | +1.204 [+0.545, +1.870] |
| ESC-50 | three_way_interaction | -1.600 [-2.750, -0.450] | -1.019 [-1.657, -0.383] |
| UrbanSound8K | AAKV_main_effect_alone_T_minus_I | -0.366 [-0.974, +0.263] | -0.487 [-0.830, -0.139] |
| UrbanSound8K | AAKV_added_to_Selector_TS_minus_S | +1.122 [+0.550, +1.695] | +0.423 [+0.088, +0.771] |
| UrbanSound8K | AAKV_added_to_FusionSelector_TFS_minus_FS | +1.443 [+0.973, +1.913] | +0.816 [+0.543, +1.086] |
| UrbanSound8K | AAKV_x_Selector_interaction_TS-T-S+I | +1.489 [+0.847, +2.130] | +0.910 [+0.557, +1.262] |
| UrbanSound8K | three_way_interaction | -0.802 [-1.477, -0.149] | -0.378 [-0.743, -0.023] |
| FSD50K | AAKV_main_effect_alone_T_minus_I | +1.759 [+0.938, +2.571] | +0.843 [+0.366, +1.315] |
| FSD50K | AAKV_added_to_Selector_TS_minus_S | +4.095 [+3.333, +4.848] | +2.044 [+1.579, +2.495] |
| FSD50K | AAKV_added_to_FusionSelector_TFS_minus_FS | +3.900 [+3.196, +4.613] | +2.324 [+1.889, +2.765] |
| FSD50K | AAKV_x_Selector_interaction_TS-T-S+I | +2.336 [+1.476, +3.206] | +1.200 [+0.713, +1.695] |
| FSD50K | three_way_interaction | -0.313 [-1.056, +0.459] | +0.141 [-0.281, +0.569] |
| AudioSet | AAKV_main_effect_alone_T_minus_I | -0.563 [-1.120, +0.000] | -0.380 [-0.725, -0.038] |
| AudioSet | AAKV_added_to_Selector_TS_minus_S | +1.259 [+0.766, +1.752] | +0.623 [+0.302, +0.939] |
| AudioSet | AAKV_added_to_FusionSelector_TFS_minus_FS | +1.277 [+0.801, +1.758] | +0.791 [+0.479, +1.110] |
| AudioSet | AAKV_x_Selector_interaction_TS-T-S+I | +1.822 [+1.247, +2.408] | +1.003 [+0.661, +1.351] |
| AudioSet | three_way_interaction | -0.656 [-1.155, -0.145] | -0.212 [-0.508, +0.087] |
| TUT2017 | AAKV_main_effect_alone_T_minus_I | +5.705 [+4.316, +7.094] | +2.621 [+1.770, +3.451] |
| TUT2017 | AAKV_added_to_Selector_TS_minus_S | +6.474 [+5.064, +7.906] | +2.996 [+2.075, +3.906] |
| TUT2017 | AAKV_added_to_FusionSelector_TFS_minus_FS | +9.038 [+7.692, +10.385] | +4.881 [+4.048, +5.716] |
| TUT2017 | AAKV_x_Selector_interaction_TS-T-S+I | +0.769 [-0.791, +2.286] | +0.374 [-0.551, +1.281] |
| TUT2017 | three_way_interaction | +3.333 [+1.752, +4.893] | +2.082 [+1.162, +2.991] |

## Evidence boundary

- Task11 already compares Direct, RawTriple, generic Qwen and AAKV under the same frozen one-hop iKnow aggregation.
- Task25 contains Direct + Fusion + Selector as `FS`, so the full AAKV method can be compared with the same method using Direct text (`TFS_Final` versus `FS`).
- Task25 does not contain RawTriple + Fusion + Selector. If the manuscript claims AAKV is superior to RawTriple inside the complete system, one additional frozen `Raw-FS` control is required.
- The manual semantic audit is not fabricated: the 180 rows are prepared, but relation-faithfulness, direction and hallucination judgments remain for human review.

## Mechanism-oriented diagnostics

`06_AAKV_prediction_flips.csv` compares AAKV wrong-to-correct versus correct-to-wrong transitions before and after selection. `07_AAKV_effect_by_selector_consensus.csv` reports the AAKV increment within low/middle/high selector-consensus strata. Consensus is a selector-confidence proxy, not ground-truth relevance, so these analyses support but do not prove a causal noise-reduction mechanism.
