#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/zkx/zkx/review1/26_relation_selection_AAKV_control
PY=/home/star/anaconda3/envs/zkx/bin/python
run(){ CUDA_VISIBLE_DEVICES="$1" "$PY" "$ROOT/code/task26_relation_selection.py" "$2" >"$ROOT/$2.log" 2>&1; }
mkdir -p "$ROOT"
run 0 03_FSD50K &
run 1 05_AudioSet &
(
  run 2 01_ESC50
  run 2 02_UrbanSound8K
  run 2 06_TUT2017
) &
wait
touch "$ROOT/workers_complete.flag"
