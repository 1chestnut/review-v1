#!/usr/bin/env bash
set -u
R=/data/zkx/zkx/review1;T="$R/25d_representative_cases";mkdir -p "$T/code"
while [ "$(find "$R/25_final_experiment_alpha03_Nr5/test" -name progress.json 2>/dev/null | wc -l)" -lt 5 ]; do sleep 30; done
/home/star/anaconda3/envs/zkx/bin/python "$T/code/task25d_case_analysis.py" >"$T/run.log" 2>&1
