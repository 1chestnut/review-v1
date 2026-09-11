#!/usr/bin/env bash
set -u
ROOT=/data/zkx/zkx/review1
TASK="$ROOT/25_final_experiment_alpha03_Nr5"
DATASETS=(01_ESC50 02_UrbanSound8K 03_FSD50K 05_AudioSet 06_TUT2017)

while true; do
  ready=1
  for dataset in "${DATASETS[@]}"; do
    if [ ! -f "$TASK/test/$dataset/progress.json" ]; then
      ready=0
      break
    fi
  done
  if [ "$ready" -eq 1 ]; then
    /home/star/anaconda3/envs/zkx/bin/python "$TASK/code/task25_summarize.py" > "$TASK/finalize.log" 2>&1
    exit $?
  fi
  sleep 30
done
