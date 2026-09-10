# Task 16 — Second-hop text structure audit

Only the textual organization of the same frozen second-hop paths is varied.

- `D-1st`: Task14 matched one-hop baseline.
- `Flat-HalfEdge`: exact Task14 `AAKV-M1-P5`; first-hop and second-edge texts are encoded separately and pooled in score space.
- `FullPath-Chained`: one complete path sentence containing origin, r1, middle, r2, and tail.
- `FullPath-TwoSentence`: verified first-hop AAKV sentence followed by verified second-edge AAKV sentence, encoded jointly as one prompt.
- `Endpoint`: origin and final tail only; relations and intermediate node are omitted.

Frozen: `K=5`, `M1=3`, `M2=1`, total `P=5`, `gamma=0.85`, no gate, identical paths, identical audio cache, identical aggregation.

This is exploratory. No per-dataset winner may be selected as the final test protocol.
