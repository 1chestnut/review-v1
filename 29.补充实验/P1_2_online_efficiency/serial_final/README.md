# P1-2 serial online efficiency profile

Five datasets were run serially on physical GPU 0 (NVIDIA GeForce RTX 4090 D).
Each dataset uses 200 evenly spaced samples from its final manifest, 20 model-warm-up samples, 5 timed repeats, and batch sizes 1 and 32.
The TUT2017 sample frame is the final 6300-record rerun, not the earlier 4680-record set.
All selected audio files were read once before timing to reduce order-dependent cold file-cache effects.
Timed latency includes live audio preprocessing/CLAP audio encoding and method-specific scoring/ranking.
Offline AAKV generation, RotatE retrieval, and CLAP text-feature/cache construction are excluded.
Offline cache size comprises precomputed label/evidence text embeddings and evidence-index mapping only; it excludes model weights and raw audio.
The manuscript summary gives dataset-equal macro means. Relative overhead is the latency ratio against CLAP at the same batch size. Throughput is 1000 divided by macro-mean latency (ms/sample).

## Final manifests

- ESC-50: `/data/zkx/zkx/review1/25_final_experiment_alpha03_Nr5/test/01_ESC50/samples.json`; SHA-256 `da87df83666b42b481ca29b5734b12af9d7e979bedd02b83d9823bf1464af806`
- UrbanSound8K: `/data/zkx/zkx/review1/25_final_experiment_alpha03_Nr5/test/02_UrbanSound8K/samples.json`; SHA-256 `f1ccc021ebf9a62e949ca0dbf60cdc9c79f08dc6877bcd6b14ab3d7bb9301dce`
- FSD50K: `/data/zkx/zkx/review1/25_final_experiment_alpha03_Nr5/test/03_FSD50K/samples.json`; SHA-256 `0713953a638661a0de0b4d6a58b576f90051de91ca42e0c5be9f491e34f9de6e`
- AudioSet: `/data/zkx/zkx/review1/25_final_experiment_alpha03_Nr5/test/05_AudioSet/samples.json`; SHA-256 `cb143b1219cc795881fa9009a2f691c3466add651dcb3293c9fbae837a42a265`
- TUT2017: `/data/zkx/zkx/review1/28_TUT2017_full6300_rerun/main/test/06_TUT2017/samples.json`; SHA-256 `d9a697805d8e59550d60e8ce132e74496f386f4960a241c98a0b17798dd11b8f`

## Artifacts

- `efficiency_by_dataset.csv`: all five datasets × two batch sizes × three methods.
- `efficiency_manuscript_summary.csv`: six macro-summary rows.
- `efficiency_section.tex`: proposed LaTeX text/table, requiring manuscript-layout review before insertion.
- Dataset folders: five-repeat timings, per-dataset summary, exact protocol, and completion marker.
