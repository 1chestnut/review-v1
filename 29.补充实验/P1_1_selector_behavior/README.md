# Final sample-level relation selection audit

This is a CPU-only recount of saved per-sample selections. No training, model inference, selector change, or factorial rerun was performed.

## Sources and checks

- ESC-50, UrbanSound8K, FSD50K, and AudioSet: `26_relation_selection_AAKV_control/<dataset>/samples.json` (`relations.AAKV-Selector5` and `relations.AAKV-FrozenRq`), cross-checked sample by sample against `25_final_experiment_alpha03_Nr5/test/<dataset>/samples.json` (`selected.TFS_Final.relations`).
- TUT2017: `28_TUT2017_full6300_rerun/selector/06_TUT2017/samples.json` (`relations.AAKV-Selector5` and `relations.AAKV-FrozenRq`), cross-checked against the 28 final main/test record. The old 4,680-sample Task25e output was not used.
- All five datasets have the requested N, consecutive unique sample indices, matching final audio paths and relation lists, five distinct selected relations per sample, and one fixed FrozenRq set per dataset.
- FrozenRq set sizes are dataset-specific: five for ESC-50 and TUT2017, six for UrbanSound8K, and four for FSD50K and AudioSet. Jaccard uses each full fixed set without truncation.
- The observed vocabulary contains 47 distinct relations. The frequency file contains all 47 for each dataset, including any with zero selections; each dataset's selected counts sum to 5N.

## Definitions

- **Unique relation sets**: number of distinct unordered Top-5 relation combinations; selection order is ignored.
- **Dominant-set share (%)**: 100 times the count of the most frequent unordered Top-5 combination divided by N.
- **Selected count/share (%)**: number/percentage of clips whose Top-5 contains a given relation. Shares over 47 relations sum to 500%, because each clip contributes five selections.
- **Mean Jaccard vs FrozenRq**: arithmetic mean across clips of |selected Top-5 intersection FrozenRq| / |selected Top-5 union FrozenRq|.
- These measures establish whether selections vary across clips; they do not by themselves establish that selection causes higher accuracy.

## Dominant sets

| Dataset | Count | Relations (unordered) | FrozenRq |
|---|---:|---|---|
| ESC-50 | 28 | caused by, emitted by, follows, is sound of, produces | belongs to class, event composed of, has children, has parent, perceived as |
| UrbanSound8K | 134 | emotionally associated with, has pitch, has timbre, is variant of, transcribed as | associated with environment, localized in, occurs in, overlaps with, part of scene, used for |
| FSD50K | 154 | affects, associated with environment, associated with event, belongs to class, can be heard in | has parent, is sound of, overlaps with, transcribed as |
| AudioSet | 259 | affects, associated with environment, associated with event, belongs to class, can be heard in | belongs to class, has children, has parent, is a type of |
| TUT2017 | 67 | event composed of, has children, has parent, has sibling, is a type of | described by, event composed of, has parent, is variant of, scene contains |

## Source SHA-256

- `/data/zkx/zkx/review1/26_relation_selection_AAKV_control/01_ESC50/samples.json`: `b48bc2431d16813e02cb52fc854aca0a1dca78f4813738b564196058441c225b`
- `/data/zkx/zkx/review1/25_final_experiment_alpha03_Nr5/test/01_ESC50/samples.json`: `da87df83666b42b481ca29b5734b12af9d7e979bedd02b83d9823bf1464af806`
- `/data/zkx/zkx/review1/26_relation_selection_AAKV_control/02_UrbanSound8K/samples.json`: `16f909026189443e8cbafc746001ce6693ebd72dd96d858e11058f0ad914d2bc`
- `/data/zkx/zkx/review1/25_final_experiment_alpha03_Nr5/test/02_UrbanSound8K/samples.json`: `f1ccc021ebf9a62e949ca0dbf60cdc9c79f08dc6877bcd6b14ab3d7bb9301dce`
- `/data/zkx/zkx/review1/26_relation_selection_AAKV_control/03_FSD50K/samples.json`: `d067aa05ee7abcbb47f677e31d2df26aaf5b5270a605cf3036134c2855ada7a0`
- `/data/zkx/zkx/review1/25_final_experiment_alpha03_Nr5/test/03_FSD50K/samples.json`: `0713953a638661a0de0b4d6a58b576f90051de91ca42e0c5be9f491e34f9de6e`
- `/data/zkx/zkx/review1/26_relation_selection_AAKV_control/05_AudioSet/samples.json`: `41edd90f05eadfbaa041ae1d99ab3f0f1ebe452a8c98dae94361b637f9aa06ec`
- `/data/zkx/zkx/review1/25_final_experiment_alpha03_Nr5/test/05_AudioSet/samples.json`: `cb143b1219cc795881fa9009a2f691c3466add651dcb3293c9fbae837a42a265`
- `/data/zkx/zkx/review1/28_TUT2017_full6300_rerun/selector/06_TUT2017/samples.json`: `ecd65aafaf063f2b79d545ae65f7070b237f2cf11997bcec05810f9169aee7fc`
- `/data/zkx/zkx/review1/28_TUT2017_full6300_rerun/main/test/06_TUT2017/samples.json`: `d9a697805d8e59550d60e8ce132e74496f386f4960a241c98a0b17798dd11b8f`
