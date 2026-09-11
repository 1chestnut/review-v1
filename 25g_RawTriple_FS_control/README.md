# Task25(g): RawTriple + Fusion + Selector control

This control uses the frozen Task25 protocol. Its only changed variable is the
knowledge verbalization:

- `FS`: Direct text (`head, tail`) + Fusion + Selector, already in Task25.
- `Raw-FS`: Raw triple (`head relation tail`) + the same Fusion + Selector.
- `TFS_Final`: AAKV + the same Fusion + Selector, already in Task25.

Frozen: CLAP, KG, strict mapping, dataset samples, K=5, M=3, alpha=0.3,
Nr=5, one hop, no Top-P, seed rule, selector algorithm, normalized-LSE fusion,
and evaluation protocol. Ground-truth labels are not used by the selector.

The experiment determines whether AAKV adds value beyond merely retaining the
relation token in a raw triple.
