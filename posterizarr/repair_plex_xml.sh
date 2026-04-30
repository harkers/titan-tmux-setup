#!/bin/bash
# Repair Plex's recurring channels-duplicate XML corruption.
# Uses busy_timeout to wait for Plex's WAL-mode lock without stopping the server.

LOG=/home/stu/projects/posterizarr/repair_plex_xml.log
DB='/home/stu/projects/plex/config/Library/Application Support/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db'

ts() { date -u +'%Y-%m-%dT%H:%M:%SZ'; }
log() { echo "[$(ts)] $*" >> "$LOG"; }

before=$(sqlite3 -cmd '.timeout 30000' "$DB" "PRAGMA busy_timeout = 30000; SELECT COUNT(*) FROM media_streams WHERE extra_data LIKE '%ma:channels%' AND channels IS NOT NULL;" 2>&1 | tail -1)
if [ "$before" -eq 0 ] 2>/dev/null; then
  log "no poisoning detected — no-op"
  exit 0
fi

log "poisoned rows before: $before"

cleaned=$(sqlite3 -cmd '.timeout 30000' "$DB" "PRAGMA busy_timeout = 30000; UPDATE media_streams SET extra_data = json_remove(extra_data, '\$.\"ma:channels\"', '\$.\"ma:bitRate\"') WHERE extra_data LIKE '%ma:channels%' AND channels IS NOT NULL; SELECT changes();" 2>&1 | tail -1)

log "cleaned: $cleaned rows"
