#!/usr/bin/env bash
set -euo pipefail
ROOT=/data/zkx/zkx/review1/25g_RawTriple_FS_control
PY=/home/star/anaconda3/envs/zkx/bin/python
RUN="$ROOT/code/task25g_rawfs_control.py"
export LD_LIBRARY_PATH=/home/star/anaconda3/envs/zkx/lib:${LD_LIBRARY_PATH:-}

CUDA_VISIBLE_DEVICES=0 "$PY" "$RUN" 03_FSD50K >"$ROOT/gpu0_FSD50K.log" 2>&1 &
echo $! >"$ROOT/gpu0.pid"

CUDA_VISIBLE_DEVICES=1 "$PY" "$RUN" 05_AudioSet >"$ROOT/gpu1_AudioSet.log" 2>&1 &
echo $! >"$ROOT/gpu1.pid"

(
  CUDA_VISIBLE_DEVICES=2 "$PY" "$RUN" 01_ESC50 >"$ROOT/gpu2_ESC50.log" 2>&1
  CUDA_VISIBLE_DEVICES=2 "$PY" "$RUN" 02_UrbanSound8K >"$ROOT/gpu2_UrbanSound8K.log" 2>&1
  CUDA_VISIBLE_DEVICES=2 "$PY" "$RUN" 06_TUT2017 >"$ROOT/gpu2_TUT2017.log" 2>&1
) &
echo $! >"$ROOT/gpu2.pid"
