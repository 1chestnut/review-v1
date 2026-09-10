# Task 21 — No-Top-P factorial ablation versus frozen iKnow

## Purpose

This task disables Top-P everywhere and compares every module directly with the frozen `iKnow-05b` baseline. It tests each module alone, every pair, and the complete method without second-hop retrieval.

## Frozen settings

- One hop only; no second-hop retrieval, decay, or gate.
- `K=5`, `M=3`, `R=1`, `kappa=100`, fixed `alpha=0.5`, seed `42`.
- `Top-P=All`: no evidence pruning in any branch.
- Same CLAP, dataset order, label space, audio embeddings, entity mapping, and candidate relations.
- The selector is label-free `Consensus-Margin-Top1`. In every selector branch it reads that branch's own score space, so toggling the selector is the only changed module.

## Methods

| Code | Text | Fusion | Relation choice | Meaning |
|---|---|---|---|---|
| CLAP | none | none | none | Original CLAP |
| I | Direct | joint NormLSE | frozen iKnow relations | Frozen iKnow-05b baseline |
| T | AAKV | joint NormLSE | frozen | Text module only |
| F | Direct | hierarchical, alpha=.5 | frozen | Fusion module only |
| S | Direct | joint NormLSE | automatic | Selector only |
| TF | AAKV | hierarchical | frozen | Text + fusion |
| TS | AAKV | joint NormLSE | automatic | Text + selector |
| FS | Direct | hierarchical | automatic | Fusion + selector |
| TFS | AAKV | hierarchical | automatic | Complete three-module method |

Every non-CLAP row reports `delta_Hit@1_vs_iKnow` and `delta_MRR_vs_iKnow`. Thus a positive delta means an improvement over the same frozen iKnow baseline, not over another intermediate experiment.
