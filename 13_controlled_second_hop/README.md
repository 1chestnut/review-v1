# Task 13: Controlled second-hop potential audit

This exploratory experiment freezes Task 12 method D as `D-1st` and changes only
the availability of filtered second-hop evidence.

- K=5, M1=3, M2=1.
- Same frozen per-dataset relation set at both hops.
- No selective gate.
- Second-hop similarity is multiplied by gamma=0.85.
- First- and second-hop evidence compete for one shared final Top-P=5 budget.
- Self-loops, returns to the class origin, duplicate entity paths and duplicate
  texts are removed before inference.
- Task 12 audio embeddings are reused exactly; audio is not re-encoded.
- Every intermediate entity must be a valid original KG entity ID. Failures are
  counted and never silently remapped from display text.

The second-hop sentence uses Task 10's deterministic verified universal fallback
form. This is an exploratory potential test, not a validation-selected final
configuration. If it is promising, M2, gamma and P must subsequently be selected
on the declared development protocol.
