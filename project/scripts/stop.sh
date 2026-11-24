#!/usr/bin/env bash
# Stop the compute run (Layer A). Jobs resume from checkpoints on next launch.
cd "$(dirname "$0")/.." || exit 1
tmux kill-session -t research 2>/dev/null
[ -f state/run_all.lock ] && { PID=$(cat state/run_all.lock); pkill -P "$PID"; kill "$PID"; rm -f state/run_all.lock; }
echo "stopped"
