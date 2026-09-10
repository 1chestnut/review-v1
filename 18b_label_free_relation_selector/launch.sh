#!/usr/bin/env bash
set -u
ROOT=/data/zkx/zkx/review1/18b_label_free_relation_selector
A=/data/zkx/zkx/review1/18a_relation_oracle_audit
PY=/home/star/anaconda3/envs/zkx/bin/python
run_one() {
 gpu="$1"; n="$2"
 CUDA_VISIBLE_DEVICES="$gpu" "$PY" "$ROOT/run_selector.py" \
  --dataset-dir "$ROOT/$n" \
  --task18a-result "$A/$n/results/relation_oracle_results.json" \
  --task18a-cache "$A/$n/results/static_relation_cache.pt" \
  --output-dir "$ROOT/$n/results" > "$ROOT/$n/run.log" 2>&1
 code=$?; printf '{"dataset":"%s","gpu":%s,"exit_code":%s,"finished_at":"%s"}\n' "$n" "$gpu" "$code" "$(date '+%F %T')" > "$ROOT/$n/run_status.json"
 return "$code"
}
case "${1:-}" in
 gpu0) run_one 0 05_AudioSet; run_one 0 04_DCASE17_T4 ;;
 gpu1) run_one 1 01_ESC50; run_one 1 03_FSD50K ;;
 gpu2) run_one 2 02_UrbanSound8K; run_one 2 06_TUT2017 ;;
 *) exit 2 ;;
esac
