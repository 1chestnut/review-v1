#!/usr/bin/env bash
set -euo pipefail

export P1_2_TASK_ROOT='/data/zkx/zkx/review1/29.补充实验/P1_2_online_efficiency/serial_final'
export CUDA_VISIBLE_DEVICES=0
export PYTHONUNBUFFERED=1

PY='/home/star/anaconda3/envs/zkx/bin/python'
CODE='/data/zkx/zkx/review1/29.补充实验/P1_2_online_efficiency/code'
mkdir -p "$P1_2_TASK_ROOT"

for dataset in ESC-50 UrbanSound8K FSD50K AudioSet TUT2017; do
    printf 'START %s %s\n' "$dataset" "$(date -Is)"
    "$PY" -u "$CODE/p1_2_efficiency.py" "$dataset"
    printf 'DONE %s %s\n' "$dataset" "$(date -Is)"
done

"$PY" "$CODE/p1_2_summarize.py"
"$PY" "$CODE/p1_2_finalize.py"
printf 'ALL_COMPLETE %s\n' "$(date -Is)"
