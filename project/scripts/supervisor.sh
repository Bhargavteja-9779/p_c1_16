#!/usr/bin/env bash
# Layer B supervisor: restarts the agent CLI headlessly until state says FINISHED.
# Usage:  nohup setsid bash scripts/supervisor.sh >/dev/null 2>&1 &
# Stop:   touch state/STOP_SUPERVISOR   (or: pkill -f scripts/supervisor.sh)
set -u
cd "$(dirname "$0")/.." || exit 1
LOG=logs/supervisor.log
mkdir -p logs
log(){ echo "[$(date -Is)] $*" >> "$LOG"; }

detect_cli(){
  if command -v claude >/dev/null 2>&1; then echo claude; return; fi
  for c in codex aider gemini; do command -v $c >/dev/null 2>&1 && { echo $c; return; }; done
  echo none
}
CLI=$(detect_cli)
if [ "$CLI" = none ]; then
  log "No agent CLI found on PATH. Auto-restart of the agent is NOT possible; paste BOOTSTRAP_PROMPT.txt manually."
  exit 2
fi
log "supervisor start (cli=$CLI, pid=$$)"
BACKOFF=(300 900 1800 3600)
i=0
while true; do
  if [ -f state/STOP_SUPERVISOR ]; then log "STOP_SUPERVISOR found; exiting"; exit 0; fi
  if grep -q '"FINISHED"' state/agent_state.json 2>/dev/null; then log "state FINISHED; exiting"; exit 0; fi
  PROMPT="$(cat BOOTSTRAP_PROMPT.txt)"
  OUT=logs/agent_run_$(date +%Y%m%d_%H%M%S).log
  log "launching agent ($CLI) -> $OUT"
  case "$CLI" in
    claude) (cd .. && claude -p "$PROMPT" --permission-mode acceptEdits) > "$OUT" 2>&1 ;;
    codex)  (cd .. && codex exec "$PROMPT") > "$OUT" 2>&1 ;;
    *)      (cd .. && $CLI "$PROMPT") > "$OUT" 2>&1 ;;
  esac
  RC=$?
  log "agent exited rc=$RC"
  if grep -q '"FINISHED"' state/agent_state.json 2>/dev/null; then log "FINISHED"; exit 0; fi
  SLEEP=${BACKOFF[$i]}
  # If the output mentions a reset time like "resets at 3pm" / epoch, try to sleep until then.
  RESET=$(grep -oiE 'reset[s]? (at|in) [^.]*' "$OUT" | head -1)
  if [ -n "$RESET" ]; then
    T=$(echo "$RESET" | sed -E 's/.*(at|in) //I')
    TS=$(date -d "$T" +%s 2>/dev/null || true)
    if [ -n "$TS" ] && [ "$TS" -gt "$(date +%s)" ]; then SLEEP=$(( TS - $(date +%s) + 60 )); fi
    log "usage-limit text: '$RESET' -> sleeping $SLEEP s"
  fi
  [ "$SLEEP" -gt 3600 ] && [ -z "$RESET" ] && SLEEP=3600
  log "sleeping $SLEEP s before restart"
  sleep "$SLEEP"
  [ $i -lt 3 ] && i=$((i+1))
  [ $RC -eq 0 ] && i=0
done
