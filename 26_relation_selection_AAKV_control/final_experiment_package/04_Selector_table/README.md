# 04_Selector_table: Frozen, frequency, random and sample-adaptive relation selection.

## Comparison
All methods use AAKV and the same Fusion. Only relation choice changes: frozen Rq, static frequency Top-5, Random5 with seeds 42/43/44, or sample-level label-free Selector5. Ground truth is used only by the evaluator.

## Frozen external inputs

The code is complete and does not import another task's runner. It reads the following immutable research assets:

- audio and labels under `/data/zkx/zkx/iknow-audio/data`;
- CLAP model files under the project model directory;
- RotatE model `/data/zkx/zkx/iknow-audio/KGE_models/001`;
- frozen audio/text tensors in `/data/zkx/zkx/review1/12_shared-abcd-statistics`;
- static KG relation-tail cache in `/data/zkx/zkx/review1/18a_relation_oracle_audit`;
- frozen AAKV dictionary `/data/zkx/zkx/review1/20A_topP5_aligned_selector_exploration/aakv_all.json`.

These are data/model inputs, not imported experiment logic. Every computational folder contains its own copy of each dataset runtime.

## Frozen protocol

One hop; K=5; M=3; alpha=0.3; Nr=5 when Selector is enabled; kappa=100; Top-P disabled; seed 42 plus SHA256(audio path). DCASE17-T4 is development-only and is not included in the five test datasets.
