#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/zkx/zkx/review1/25g_RawTriple_FS_control
while true; do
  complete=0
  for dataset in 01_ESC50 02_UrbanSound8K 03_FSD50K 05_AudioSet 06_TUT2017; do
    if [ -f "$ROOT/$dataset/progress.json" ]; then
      complete=$((complete + 1))
    fi
  done
  if [ "$complete" -eq 5 ]; then break; fi
  sleep 30
done
/home/star/anaconda3/envs/zkx/bin/python "$ROOT/code/task25g_finalize.py" >"$ROOT/finalize.log" 2>&1
