#!/usr/bin/env bash
# travel-mode — pause bandwidth-hungry workloads on titan for travel.
#
# Usage:
#   travel-mode on       — pause heavy containers + cron entries
#   travel-mode off      — resume them
#   travel-mode status   — show what's currently paused
#
# Conservative by default: only stops AI/agent/embedding workloads and
# heavy Plex maintenance crons. Leaves user-facing services (Plex,
# Posterizarr, Nextcloud, Pi-hole, Nitter), data stores (Redis, Qdrant,
# Vault), and infrastructure (Caddy, cloudflared) running.
#
# State lives in ~/.travel-mode/ — check it if anything looks off.

set -uo pipefail

STATE_DIR="${HOME}/.travel-mode"
PAUSED_LIST="${STATE_DIR}/paused-containers.txt"
CRONTAB_BAK="${STATE_DIR}/crontab.bak"
LOG="${STATE_DIR}/travel-mode.log"

mkdir -p "$STATE_DIR"

# ─── what to pause when ON ────────────────────────────────────────────────

# Container name patterns (regex, OR'd together).
# Edit if your workloads change.
PAUSE_CONTAINER_PATTERNS=(
    '^ollama'
    '^kometa-'
    '^openclaw-.*-(agent|deployer|sbx|embedding|docling|selenium|powerpoint)'
    '^openclaw-.*-mcp$'
)

# Cron line substring filters (case-insensitive).
PAUSE_CRON_PATTERNS=(
    'kometa'
    'posterizarr-cycle'
    'plex-overlay-sync'
    'tmdb-enrich'
)

# ─── helpers ──────────────────────────────────────────────────────────────

log() { echo "[$(date -Is)] $*" | tee -a "$LOG"; }
die() { log "ERR: $*"; exit 1; }

list_matching_containers() {
    docker ps --format '{{.Names}}' 2>/dev/null | while read -r name; do
        for pat in "${PAUSE_CONTAINER_PATTERNS[@]}"; do
            if echo "$name" | grep -qE "$pat"; then
                echo "$name"
                break
            fi
        done
    done
}

# ─── ON ───────────────────────────────────────────────────────────────────

travel_mode_on() {
    if [ -s "$PAUSED_LIST" ]; then
        die "already on (paused list exists at $PAUSED_LIST). Run 'off' first."
    fi

    log "==> travel-mode ON"

    # 1. Pause containers
    : > "$PAUSED_LIST"
    list_matching_containers | sort -u > "$PAUSED_LIST.tmp"
    n=$(wc -l < "$PAUSED_LIST.tmp")
    if [ "$n" -gt 0 ]; then
        log "stopping $n containers..."
        while read -r name; do
            if docker stop "$name" >/dev/null 2>&1; then
                echo "$name" >> "$PAUSED_LIST"
                log "  stopped $name"
            else
                log "  WARN failed to stop $name"
            fi
        done < "$PAUSED_LIST.tmp"
        rm -f "$PAUSED_LIST.tmp"
    else
        log "no matching containers to stop"
        rm -f "$PAUSED_LIST.tmp"
    fi

    # 2. Pause cron entries by commenting them out
    if crontab -l >/dev/null 2>&1; then
        crontab -l > "$CRONTAB_BAK"
        log "crontab backed up to $CRONTAB_BAK"

        local pattern_re
        pattern_re=$(IFS='|'; echo "${PAUSE_CRON_PATTERNS[*]}")
        local newcron commented
        newcron=$(mktemp)
        commented=0
        while IFS= read -r line; do
            if [[ ! "$line" =~ ^# ]] && echo "$line" | grep -qiE "$pattern_re"; then
                echo "# travel-mode-paused: $line" >> "$newcron"
                commented=$((commented + 1))
                log "  commented: $line"
            else
                echo "$line" >> "$newcron"
            fi
        done < "$CRONTAB_BAK"
        if [ "$commented" -gt 0 ]; then
            crontab "$newcron"
            log "$commented cron entries commented out"
        else
            log "no matching cron entries"
        fi
        rm -f "$newcron"
    else
        log "no user crontab to modify"
    fi

    # 3. Reminder
    cat <<EOF

travel-mode is ON.
Manual reminders not automated:
  - In Plex web → Settings → Network → Remote Streaming Quality, cap at 4 Mbps
  - On Mac, switch Tailscale exit-node to Forge if available
  - Run 'travel-mode off' when home

State: $STATE_DIR
EOF
}

# ─── OFF ──────────────────────────────────────────────────────────────────

travel_mode_off() {
    log "==> travel-mode OFF"

    # 1. Restore containers
    if [ -s "$PAUSED_LIST" ]; then
        n=$(wc -l < "$PAUSED_LIST")
        log "restarting $n containers..."
        while read -r name; do
            if docker start "$name" >/dev/null 2>&1; then
                log "  started $name"
            else
                log "  WARN failed to start $name (may have been removed)"
            fi
        done < "$PAUSED_LIST"
        : > "$PAUSED_LIST"
    else
        log "no paused containers to restart"
    fi

    # 2. Restore crontab
    if [ -s "$CRONTAB_BAK" ]; then
        crontab "$CRONTAB_BAK"
        log "crontab restored from $CRONTAB_BAK"
        rm -f "$CRONTAB_BAK"
    else
        log "no crontab backup to restore"
    fi

    log "travel-mode is OFF — workloads resumed"
}

# ─── STATUS ───────────────────────────────────────────────────────────────

travel_mode_status() {
    if [ -s "$PAUSED_LIST" ]; then
        echo "travel-mode: ON"
        n=$(wc -l < "$PAUSED_LIST")
        echo "  $n containers currently paused:"
        sed 's/^/    /' "$PAUSED_LIST"
    else
        echo "travel-mode: OFF"
    fi
    if [ -s "$CRONTAB_BAK" ]; then
        echo "  crontab backup present at $CRONTAB_BAK"
    fi
    echo
    echo "Containers that match current pause patterns (would be stopped on 'on'):"
    list_matching_containers | sort -u | sed 's/^/  /'
}

# ─── dispatch ─────────────────────────────────────────────────────────────

case "${1:-}" in
    on) travel_mode_on ;;
    off) travel_mode_off ;;
    status) travel_mode_status ;;
    *)
        cat <<EOF
travel-mode — pause bandwidth-hungry workloads for travel

Usage: travel-mode {on|off|status}

  on      — stop matching containers + pause matching cron entries
  off     — restore containers and crontab from saved state
  status  — show whether currently ON, what's paused, what would match

State: $STATE_DIR
EOF
        exit 1
        ;;
esac
