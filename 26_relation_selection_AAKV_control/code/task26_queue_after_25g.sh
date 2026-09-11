#!/usr/bin/env bash
set -euo pipefail
PREV=/data/zkx/zkx/review1/25g_RawTriple_FS_control/summary_complete.json
ROOT=/data/zkx/zkx/review1/26_relation_selection_AAKV_control
while [ ! -f "$PREV" ]; do sleep 30; done
nohup bash "$ROOT/code/task26_launch.sh" >"$ROOT/launch.log" 2>&1 </dev/null &
echo $! >"$ROOT/launcher.pid"
