#!/usr/bin/env bash
set -u
R=/data/zkx/zkx/review1
T="$R/25a_fair_cached_efficiency"
mkdir -p "$T/code"
# Do not overlap timing with Task25 or with any other process launched by this protocol.
while pgrep -f '/data/zkx/zkx/review1/task25_run.py' >/dev/null; do sleep 30; done
for ds in 01_ESC50 02_UrbanSound8K 03_FSD50K 05_AudioSet 06_TUT2017; do
  CUDA_VISIBLE_DEVICES=0 /home/star/anaconda3/envs/zkx/bin/python "$T/code/task25a_efficiency.py" "$ds" >"$T/${ds}.log" 2>&1 || exit $?
done
/home/star/anaconda3/envs/zkx/bin/python "$T/code/task25a_summarize.py" >"$T/summarize.log" 2>&1
