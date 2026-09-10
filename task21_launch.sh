#!/usr/bin/env bash
set -u
ROOT=/data/zkx/zkx/review1
TASK="$ROOT/21_noTopP_factorial_vs_frozen_iKnow"
mkdir -p "$TASK"

nohup bash -c "CUDA_VISIBLE_DEVICES=0 /home/star/anaconda3/envs/zkx/bin/python '$ROOT/task21_run.py' 01_ESC50 >'$TASK/01_ESC50.log' 2>&1 && CUDA_VISIBLE_DEVICES=0 /home/star/anaconda3/envs/zkx/bin/python '$ROOT/task21_run.py' 05_AudioSet >'$TASK/05_AudioSet.log' 2>&1" >"$TASK/gpu0_queue.log" 2>&1 & echo $! >"$TASK/gpu0_queue.pid"
nohup bash -c "CUDA_VISIBLE_DEVICES=1 /home/star/anaconda3/envs/zkx/bin/python '$ROOT/task21_run.py' 02_UrbanSound8K >'$TASK/02_UrbanSound8K.log' 2>&1 && CUDA_VISIBLE_DEVICES=1 /home/star/anaconda3/envs/zkx/bin/python '$ROOT/task21_run.py' 04_DCASE17_T4 >'$TASK/04_DCASE17_T4.log' 2>&1" >"$TASK/gpu1_queue.log" 2>&1 & echo $! >"$TASK/gpu1_queue.pid"
nohup bash -c "CUDA_VISIBLE_DEVICES=2 /home/star/anaconda3/envs/zkx/bin/python '$ROOT/task21_run.py' 03_FSD50K >'$TASK/03_FSD50K.log' 2>&1 && CUDA_VISIBLE_DEVICES=2 /home/star/anaconda3/envs/zkx/bin/python '$ROOT/task21_run.py' 06_TUT2017 >'$TASK/06_TUT2017.log' 2>&1" >"$TASK/gpu2_queue.log" 2>&1 & echo $! >"$TASK/gpu2_queue.pid"
