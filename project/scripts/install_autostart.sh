#!/usr/bin/env bash
# Install boot/login autostart for Layer A (compute) and optionally Layer B (supervisor).
# Usage: bash scripts/install_autostart.sh [--with-supervisor]
P="$(cd "$(dirname "$0")/.." && pwd)"
TMP=$(mktemp)
crontab -l 2>/dev/null | grep -v "# research-loop" > "$TMP"
echo "@reboot cd $P && bash scripts/launch.sh # research-loop" >> "$TMP"
echo "*/5 * * * * bash $P/scripts/watchdog.sh # research-loop" >> "$TMP"
echo "17 3 * * * bash $P/scripts/snapshot.sh # research-loop" >> "$TMP"
if [ "${1:-}" = "--with-supervisor" ]; then
  echo "@reboot cd $P && nohup setsid bash scripts/supervisor.sh >/dev/null 2>&1 # research-loop" >> "$TMP"
fi
crontab "$TMP" && echo "installed crontab entries:" && crontab -l | grep research-loop
rm -f "$TMP"
