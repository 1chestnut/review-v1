#!/usr/bin/env bash
set -u
R=/data/zkx/zkx/review1;T="$R/25_final_experiment_alpha03_Nr5";mkdir -p "$T/test" "$T/validation"
cp "$R/23C_DCASE_validation_expanded_Nr/validation_grid_hit1_first.csv" "$T/validation/DCASE_grid.csv"
cp "$R/23C_DCASE_validation_expanded_Nr/selected_config_hit1_first.json" "$T/validation/selected_config.json"
nohup bash -c "CUDA_VISIBLE_DEVICES=0 /home/star/anaconda3/envs/zkx/bin/python '$R/task25_run.py' 01_ESC50 >'$T/01_ESC50.log' 2>&1 && CUDA_VISIBLE_DEVICES=0 /home/star/anaconda3/envs/zkx/bin/python '$R/task25_run.py' 05_AudioSet >'$T/05_AudioSet.log' 2>&1" >"$T/gpu0.log" 2>&1 & echo $! >"$T/gpu0.pid"
nohup bash -c "CUDA_VISIBLE_DEVICES=1 /home/star/anaconda3/envs/zkx/bin/python '$R/task25_run.py' 02_UrbanSound8K >'$T/02_UrbanSound8K.log' 2>&1" >"$T/gpu1.log" 2>&1 & echo $! >"$T/gpu1.pid"
nohup bash -c "CUDA_VISIBLE_DEVICES=2 /home/star/anaconda3/envs/zkx/bin/python '$R/task25_run.py' 03_FSD50K >'$T/03_FSD50K.log' 2>&1 && CUDA_VISIBLE_DEVICES=2 /home/star/anaconda3/envs/zkx/bin/python '$R/task25_run.py' 06_TUT2017 >'$T/06_TUT2017.log' 2>&1" >"$T/gpu2.log" 2>&1 & echo $! >"$T/gpu2.pid"
