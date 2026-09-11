#!/usr/bin/env bash
set -u
R=/data/zkx/zkx/review1
T="$R/25a_fair_cached_efficiency"
mkdir -p "$T/code"
# Do not overlap timing with Task25. Each dataset keeps all three methods on one GPU.
while pgrep -f '/data/zkx/zkx/review1/task25_run.py' >/dev/null; do sleep 30; done
CUDA_VISIBLE_DEVICES=0 /home/star/anaconda3/envs/zkx/bin/python "$T/code/task25a_efficiency.py" 01_ESC50 >"$T/01_ESC50.log" 2>&1 && \
CUDA_VISIBLE_DEVICES=0 /home/star/anaconda3/envs/zkx/bin/python "$T/code/task25a_efficiency.py" 05_AudioSet >"$T/05_AudioSet.log" 2>&1 & p0=$!
CUDA_VISIBLE_DEVICES=1 /home/star/anaconda3/envs/zkx/bin/python "$T/code/task25a_efficiency.py" 02_UrbanSound8K >"$T/02_UrbanSound8K.log" 2>&1 & p1=$!
CUDA_VISIBLE_DEVICES=2 /home/star/anaconda3/envs/zkx/bin/python "$T/code/task25a_efficiency.py" 03_FSD50K >"$T/03_FSD50K.log" 2>&1 && \
CUDA_VISIBLE_DEVICES=2 /home/star/anaconda3/envs/zkx/bin/python "$T/code/task25a_efficiency.py" 06_TUT2017 >"$T/06_TUT2017.log" 2>&1 & p2=$!
printf '%s\n' "$p0" >"$T/gpu0.pid";printf '%s\n' "$p1" >"$T/gpu1.pid";printf '%s\n' "$p2" >"$T/gpu2.pid"
wait "$p0";s0=$?;wait "$p1";s1=$?;wait "$p2";s2=$?
if [ "$s0" -ne 0 ] || [ "$s1" -ne 0 ] || [ "$s2" -ne 0 ]; then exit 1; fi
/home/star/anaconda3/envs/zkx/bin/python "$T/code/task25a_summarize.py" >"$T/summarize.log" 2>&1
