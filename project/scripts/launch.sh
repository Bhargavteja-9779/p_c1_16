#!/usr/bin/env bash
# Detached launch of the compute run (Layer A). Safe to call repeatedly (lock => no-op if running).
cd "$(dirname "$0")/.." || exit 1
mkdir -p logs
if command -v tmux >/dev/null && ! tmux has-session -t research 2>/dev/null; then
  tmux new-session -d -s research "python3 run_all.py --mode full --resume ${*} >> logs/run_all.stdout 2>&1"
  echo "launched in tmux session 'research' (attach: tmux attach -t research)"
else
  nohup setsid python3 run_all.py --mode full --resume "$@" >> logs/run_all.stdout 2>&1 < /dev/null &
  echo "launched with nohup/setsid pid $!"
fi
