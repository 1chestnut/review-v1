# Task 25(d) - Representative per-sample case analysis

This task is a post-hoc explanation of the frozen Task25 predictions. Ground-truth labels are used only after inference to categorize outcomes; they never enter relation selection, AAKV generation, fusion, or prediction.

Four strict case groups are reported: AAKV-only rescue, selector-only rescue, rescue achieved only by the complete TFS combination, and failures where frozen iKnow was correct but TFS became wrong. Up to three representative cases per group are selected by reciprocal-rank change while preferring different datasets.

Each displayed case contains the audio path, ground truth, CLAP prediction, frozen-iKnow prediction, relevant module prediction, Final-TFS prediction, selected relations, ranks of all Task25 branches, and auditable AAKV evidence. Evidence is labeled precisely: the displayed item is the Top-1 KGE-ranked tail within each selected relation, not a ground-truth-selected explanation.
