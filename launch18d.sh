#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/zkx/zkx/review1
SRC=$ROOT/18c_discriminative_relation_selector
OUT=$ROOT/18d_ranked_consensus
RUN=$ROOT/18d_ranked_consensus.py
run_one() {
  local gpu="$1" name="$2"
  mkdir -p "$OUT/$name/results"
  CUDA_VISIBLE_DEVICES="$gpu" python "$RUN" \
    --dataset-dir "$SRC/$name" \
    --task18a-result "$ROOT/18a_relation_oracle_audit/$name/results/relation_oracle_results.json" \
    --task18a-cache "$ROOT/18a_relation_oracle_audit/$name/results/static_relation_cache.pt" \
    --output-dir "$OUT/$name/results" \
    > "$OUT/$name/run.log" 2>&1
}
case "${1:-}" in
  0) run_one 0 01_ESC50; run_one 0 05_AudioSet ;;
  1) run_one 1 02_UrbanSound8K; run_one 1 04_DCASE17_T4 ;;
  2) run_one 2 03_FSD50K; run_one 2 06_TUT2017 ;;
  *) echo "usage: $0 {0|1|2}"; exit 2 ;;
esac
