#!/bin/bash
# posterizarr/cycle.sh — keep Posterizarr alive by restarting Plex when it hangs.
#
# Logic:
#   1. If Posterizarr is making progress (log line in last 5 min) → exit, no action needed
#   2. If asset count >= 14000 → Posterizarr near-done, exit (auto-disable)
#   3. Else: kill stuck Posterizarr, restart Plex, wait for healthy, restart Posterizarr
#
# Run via cron every 4 hours; idempotent.
set -uo pipefail

LOG=/home/stu/projects/posterizarr/cycle.log
ASSETS=/home/stu/projects/posterizarr/assets
POSTERIZARR_LOG=/config/Logs/Scriptlog.log

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }
log() { echo "[$(ts)] $*" >> "$LOG"; }

log "=== cycle start ==="

# 1. Check if asset target reached
asset_count=$(find "$ASSETS" -type f 2>/dev/null | wc -l)
log "asset count: $asset_count"
if [ "$asset_count" -ge 14000 ]; then
  log "asset count >= 14000 — done, no restart needed. Disabling cron self."
  # Remove the cron file once we hit the target
  sudo rm -f /etc/cron.d/posterizarr-cycle 2>/dev/null
  exit 0
fi

# 2. Check if Posterizarr is actively making progress
last_log_ts=$(docker exec posterizarr tail -5 "$POSTERIZARR_LOG" 2>/dev/null \
  | grep -oE "\[2026-[0-9-]+ [0-9:]+\]" | tail -1 \
  | tr -d "[]")
if [ -n "$last_log_ts" ]; then
  log "last posterizarr log line: $last_log_ts"
  last_epoch=$(date -d "$last_log_ts" +%s 2>/dev/null || echo 0)
  now_epoch=$(date +%s)
  age=$(( now_epoch - last_epoch ))
  log "log age: ${age}s"
  if [ "$age" -lt 300 ] && [ "$age" -gt 0 ]; then
    log "Posterizarr still active (log age < 5 min) — no restart"
    exit 0
  fi
fi

# 3. Stuck or hung — restart cycle
log "Posterizarr hung or no recent activity — restarting Plex + Posterizarr"

docker exec posterizarr pkill -f Posterizarr.ps1 2>/dev/null || true
sleep 2
docker exec posterizarr rm -f /config/temp/Posterizarr.Running 2>/dev/null || true

docker restart plex >> "$LOG" 2>&1
log "Plex restarted, waiting for healthy"

for i in $(seq 1 20); do
  status=$(curl -s --max-time 5 http://localhost:32400/identity -o /dev/null -w "%{http_code}" 2>&1)
  if [ "$status" = "200" ]; then
    log "Plex back at attempt $i (200 OK)"
    break
  fi
  sleep 5
done

if [ "$status" != "200" ]; then
  log "ERROR: Plex did not return 200 after 100s — aborting cycle"
  exit 1
fi

docker exec -d posterizarr pwsh /app/Posterizarr.ps1
sleep 5
log "Posterizarr restarted"

new_count=$(find "$ASSETS" -type f 2>/dev/null | wc -l)
log "cycle done; asset count now $new_count (delta from start: $((new_count - asset_count)))"
