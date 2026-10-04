# Teacher-comment language audit: main-4, 2026-10-04

## Scope and rules

Audited the files actually included by main-4, not the retired standalone Discussion source. Related Work was inspected but left unchanged as requested. Changes are marked with `teacherrevision` (red); prior black text stays black. This is a wording audit, not a change to evidence, experimental protocols, or conclusions.

Direct observations use explicit subjects and outcomes. Statistical conclusions retain the test and error-control details. Proposed explanations retain uncertainty. Technical uses of “support” (a relation voting for a class), model capabilities, and funding acknowledgments are not defensive hedges.

## Decisions on support and its variants

| Location / original phrase | Decision | Evidence or reason |
|---|---|---|
| Abstract: “These results support adapting graph evidence…” | Retain | A calibrated overall implication; does not claim independent validation of every mechanism. |
| Introduction: graph knowledge “can support audio classification” | Retain | Capability attributed to cited iKnow-audio, not an experimental scope hedge. |
| Introduction: “further support … under the evaluated settings” | Replace | State that the controlled comparisons identify contributions to classification performance; remove repeated scope phrase. |
| 4.2: iKnow† “support the value … Under the common evaluation protocol” | Replace | Table 1 directly shows higher Hit@1/MRR than CLAP. Name this comparison and its result. |
| 4.3.1: “support the contribution … within the combined configuration” | Replace | Table 2 shows lower mean Hit@1/MRR after removal of each component. Report that observation. |
| 4.3.2: “With knowledge texts and fusion rules fixed … supports selecting…” | Delete repeated sentence | Control conditions already appear at the subsection opening; comparative result already stated. |
| 4.3.2: “Table 3 supports the effectiveness…” | Delete repeated sentence | The subsection already reports every dataset's direction and the mean gains. |
| 4.3.2 statistics: “controlled comparison … supports the classification benefit…” | Combine with diversity sentence | Distinguish variation in sets from the classification comparison without repeating effectiveness claims. |
| 4.3.3: “comparison likewise supports the importance…” | Replace | State observed differences across text representations. Keep the following mechanism explanation tentative. |
| 4.4.1: intervals “supporting … under resampling…” | Delete repeated sentence | Preceding sentence already says all intervals are above zero; bootstrap interpretation follows. |
| 4.4.2: tests “support SAKI's Hit@1 advantage…” | Replace | Correctly state statistical significance after Holm correction; do not turn statistical evidence into mechanistic proof. |
| Conclusion: “Under the evaluated settings … support coordinating…” | Replace | Summarize how the framework integrates knowledge with CLAP; research scope is already in 4.5. |
| Method: predictions “support that class”; “supporting/nonsupporting groups” | Retain | Operational definition of voting and sorting, not cautious prose. |
| 4.3.2: relations “supporting the consensus class” | Retain | Same operational voting meaning. |
| Related Work: AudioCLIP/Wav2CLIP “support matching”; SLAP “supports variable audio durations” | Retain; no edits | Capability descriptions, not defensive conclusions; source wording is separately protected. |
| Acknowledgments: “was supported” | Retain | Funding statement. |

## Scope phrases and other tentative wording

| Phrase / location | Decision |
|---|---|
| 4.2 “Under this protocol” | Remove; experimental protocol is established in 4.1. |
| 4.2 “under the evaluated inference configurations” | Remove; identify the shared backbone/resources and the differing processing steps directly. |
| 4.3 opening: same CLAP, graph, classes, mapping, retrieval | Retain; necessary controls across ablations. |
| 4.3.2 opening: identical knowledge representation and fusion | Retain once; identifies the manipulated variable. |
| 4.3.3 opening: same relation selection algorithm and fusion rules | Retain once; needed because representations produce their own relation-specific scores, rather than forcing identical selected sets. |
| 4.3.3 “within the same inference procedure” at paragraph end | Remove redundant condition; retain what each text representation supplies. |
| 4.3.3 “limited benefit in this experiment, suggesting…” | Replace with the specific mean-metric result and a calibrated interpretation using “indicating.” |
| Bootstrap: models and inference settings held fixed | Retain; defines what the intervals quantify, not merely a disclaimer. |
| Parameter sensitivity: “within this search range,” “within the tested range” | Retain; a finite grid does not establish global invariance or monotonicity. |
| Case-table caption: no independent contribution established | Move to 4.5; the caption now describes the actual cached evidence. |
| Consensus/model-bias discussion after case study | Move to 4.5; retain only the observed degradation in the case analysis. |
| Cost analysis: “In these measurements” | Remove; table and timing protocol already identify the measurements. |
| “may help explain AAKV's gains” | Retain; encoder-level mechanism has not been separately tested. |
| Introduction “may vary / may alter” | Retain; motivates the question rather than claiming universal harm. |
| Conclusion “can improve” | Retain; bounded capability claim rather than guaranteed per-sample improvement. |
| “only” in label use / parameter selection | Retain; factual protocol restrictions, not lack of confidence. |

Avoid replacing every cautious verb with “show.” Some redundant conclusions were deleted; others now directly report higher/lower scores. “Indicate” remains appropriate for interpretations beyond the table's literal observation.

## Verification

Experimental values, table bodies, formula blocks, citation keys, and framework image are protected. Removed conclusions do not alter the result directions. The table-float registration and small space reservations are adjusted only to keep first numbered discussions with their tables after text shortening.
