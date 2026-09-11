#!/usr/bin/env bash
set -u
ROOT=/data/zkx/zkx/review1
TASK="$ROOT/23D_five_test_extended_Nr_sensitivity"
mkdir -p "$TASK"
nohup bash -c "CUDA_VISIBLE_DEVICES=0 /home/star/anaconda3/envs/zkx/bin/python '$ROOT/task23d_runner.py' 01_ESC50 >'$TASK/01_ESC50.log' 2>&1 && CUDA_VISIBLE_DEVICES=0 /home/star/anaconda3/envs/zkx/bin/python '$ROOT/task23d_runner.py' 05_AudioSet >'$TASK/05_AudioSet.log' 2>&1" >"$TASK/gpu0.log" 2>&1 & echo $! >"$TASK/gpu0.pid"
nohup bash -c "CUDA_VISIBLE_DEVICES=1 /home/star/anaconda3/envs/zkx/bin/python '$ROOT/task23d_runner.py' 02_UrbanSound8K >'$TASK/02_UrbanSound8K.log' 2>&1" >"$TASK/gpu1.log" 2>&1 & echo $! >"$TASK/gpu1.pid"
nohup bash -c "CUDA_VISIBLE_DEVICES=2 /home/star/anaconda3/envs/zkx/bin/python '$ROOT/task23d_runner.py' 03_FSD50K >'$TASK/03_FSD50K.log' 2>&1 && CUDA_VISIBLE_DEVICES=2 /home/star/anaconda3/envs/zkx/bin/python '$ROOT/task23d_runner.py' 06_TUT2017 >'$TASK/06_TUT2017.log' 2>&1" >"$TASK/gpu2.log" 2>&1 & echo $! >"$TASK/gpu2.pid"
