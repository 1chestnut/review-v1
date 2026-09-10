#!/usr/bin/env bash
set -u
ROOT=/data/zkx/zkx/review1/18a_relation_oracle_audit
SRC=/data/zkx/zkx/review1/05b_strict-map-k5m3-freeze
PY=/home/star/anaconda3/envs/zkx/bin/python

run_one() {
  gpu="$1"
  name="$2"
  CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/run_relation_oracle.py" \
    --dataset-dir "$ROOT/$name" \
    --source-result "$SRC/$name/results/clap_iknow_results.json" \
    --mapping "$ROOT/entity_mapping_v2.json" \
    --output-dir "$ROOT/$name/results" \
    > "$ROOT/$name/run.log" 2>&1
  code=$?
  printf '{"dataset":"%s","gpu":%s,"exit_code":%s,"finished_at":"%s"}\n' \
    "$name" "$gpu" "$code" "$(date '+%F %T')" > "$ROOT/$name/run_status.json"
  return "$code"
}

case "${1:-}" in
  gpu0) run_one 0 05_AudioSet; run_one 0 04_DCASE17_T4 ;;
  gpu1) run_one 1 03_FSD50K; run_one 1 01_ESC50 ;;
  gpu2) run_one 2 02_UrbanSound8K; run_one 2 06_TUT2017 ;;
  *) echo "usage: $0 gpu0|gpu1|gpu2"; exit 2 ;;
esac
