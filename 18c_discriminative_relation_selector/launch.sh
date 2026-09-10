#!/usr/bin/env bash
set -u
R=/data/zkx/zkx/review1/18c_discriminative_relation_selector
A=/data/zkx/zkx/review1/18a_relation_oracle_audit
B=/data/zkx/zkx/review1/18b_label_free_relation_selector
PY=/home/star/anaconda3/envs/zkx/bin/python
one(){ g="$1";n="$2"; CUDA_VISIBLE_DEVICES="$g" "$PY" "$R/run.py" --dataset-dir "$R/$n" --task18a-result "$A/$n/results/relation_oracle_results.json" --task18a-cache "$A/$n/results/static_relation_cache.pt" --output-dir "$R/$n/results" >"$R/$n/run.log" 2>&1; c=$?; printf '{"dataset":"%s","gpu":%s,"exit_code":%s,"finished_at":"%s"}\n' "$n" "$g" "$c" "$(date '+%F %T')" >"$R/$n/run_status.json"; return "$c"; }
wait_b(){ pidfile="$B/gpu$1_queue.pid"; while test -f "$pidfile" && kill -0 "$(cat "$pidfile")" 2>/dev/null; do sleep 30; done; }
case "${1:-}" in
 gpu0) wait_b 0; one 0 05_AudioSet; one 0 04_DCASE17_T4;;
 gpu1) wait_b 1; one 1 01_ESC50; one 1 03_FSD50K;;
 gpu2) wait_b 2; one 2 02_UrbanSound8K; one 2 06_TUT2017;;
 *) exit 2;;
esac
