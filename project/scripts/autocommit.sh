#!/usr/bin/env bash
# Periodic persistence of running state (Layer A results only; agent-edited files are committed by the agent).
# Stops when no run_all.py is alive and nothing is pending. Usage: nohup setsid bash scripts/autocommit.sh &
cd "$(dirname "$0")/.." || exit 1
BR=$(git rev-parse --abbrev-ref HEAD)
while true; do
  sleep 900
  git add state/queue.json state/heartbeat state/budget.json results tables logs/run_all.log 2>/dev/null
  if ! git diff --cached --quiet; then
    git commit -q -m "cycle3/session8: running-state update (queue/heartbeat/results)" && \
      for i in 1 2 3 4; do git push -q origin "$BR" && break; sleep $((i*15)); done
  fi
  pgrep -f "run_all.py" >/dev/null || break
done
