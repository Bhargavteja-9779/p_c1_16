#!/usr/bin/env bash
# Remove all autostart entries (both layers) and stop running loops.
TMP=$(mktemp); crontab -l 2>/dev/null | grep -v "# research-loop" > "$TMP"; crontab "$TMP"; rm -f "$TMP"
cd "$(dirname "$0")/.." && touch state/STOP_SUPERVISOR
pkill -f scripts/supervisor.sh 2>/dev/null
echo "autostart removed; supervisor stopped. Compute run (if any) keeps running: stop with bash scripts/stop.sh"
