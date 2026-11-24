#!/usr/bin/env bash
# Watchdog: if run_all lock is held but heartbeat is older than 20 min, kill and resume.
# Intended for cron: */5 * * * * bash /path/to/project/scripts/watchdog.sh
cd "$(dirname "$0")/.." || exit 1
HB=state/heartbeat; LOCK=state/run_all.lock
[ -f "$LOCK" ] || exit 0
AGE=$(( $(date +%s) - $(stat -c %Y "$HB" 2>/dev/null || echo 0) ))
if [ "$AGE" -gt 1200 ]; then
  PID=$(cat "$LOCK")
  echo "[$(date -Is)] heartbeat stale ${AGE}s; killing $PID and resuming" >> logs/watchdog.log
  pkill -P "$PID" 2>/dev/null; kill "$PID" 2>/dev/null; sleep 5; kill -9 "$PID" 2>/dev/null
  rm -f "$LOCK"
  bash scripts/launch.sh
fi
