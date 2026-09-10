# Task 15B — conservative post-retrieval acceptance gates

Offline controlled comparison using frozen Task 14 scores. Every real rule is
label-free, but it runs after second-hop scores exist and therefore tests noise
control, not inference-time savings. The fixed update is AAKV M2=1, shared P=5,
gamma=0.85. Only acceptance versus fallback to D-1st changes.
