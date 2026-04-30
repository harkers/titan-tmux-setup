# travel-mode — bandwidth saver for trips

A single shell script that pauses bandwidth-hungry workloads on titan for the duration of a trip. Run `travel-mode on` the morning you fly, `travel-mode off` when home.

## What it does

**On `travel-mode on`:**
- Stops Docker containers matching AI/agent/embedding/MCP patterns (`ollama*`, `kometa-*`, `openclaw-*-agent`, `openclaw-*-mcp`, etc.)
- Comments out matching crontab lines (`kometa`, `posterizarr-cycle`, `plex-overlay-sync`, `tmdb-enrich`)
- Backs up state to `~/.travel-mode/` so `off` can restore exactly

**On `travel-mode off`:**
- Restarts every container that was paused
- Reverts crontab from the backup
- Removes the state files

**Always running (never paused):**
- Plex Media Server, Posterizarr, Jellyfin, ErsatzTV — user-facing media
- OpenClaw Nextcloud, Nitter, Pi-hole — user-facing services
- Redis, Qdrant, Vault — data stores
- Caddy, cloudflared — reverse proxy + tunnels
- All `*-gateway` MCP gateways — lightweight protocol bridges

## Install

Symlink so it's on your PATH:

```bash
ssh titan
ln -sf /home/stu/projects/travel-mode/travel-mode.sh /home/stu/bin/travel-mode
chmod +x /home/stu/projects/travel-mode/travel-mode.sh
travel-mode status
```

If `~/bin` isn't on your PATH yet, add it to `~/.bashrc`:

```bash
export PATH="$HOME/bin:$PATH"
```

## Usage

```bash
travel-mode status            # see what's currently paused + what would match
travel-mode on                # the morning you fly
travel-mode off               # when you're home and connected to home WiFi
```

## Logs and state

```
~/.travel-mode/
├── paused-containers.txt    # one name per line, written by `on`
├── crontab.bak              # full crontab snapshot from before `on`
└── travel-mode.log          # append-only log of every action
```

The script refuses to run `on` twice — if `paused-containers.txt` exists with content, you must run `off` first to avoid double-bookkeeping.

## Customisation

Edit the two arrays near the top of `travel-mode.sh`:

```bash
PAUSE_CONTAINER_PATTERNS=(
    '^ollama'
    '^kometa-'
    '^openclaw-.*-(agent|deployer|sbx|embedding|docling|selenium|powerpoint)'
    '^openclaw-.*-mcp$'
)

PAUSE_CRON_PATTERNS=(
    'kometa'
    'posterizarr-cycle'
    'plex-overlay-sync'
    'tmdb-enrich'
)
```

Container patterns are regex (Bash extended). Cron patterns are case-insensitive substring matches against the cron line.

To preview what would be paused without committing:

```bash
travel-mode status   # shows "would be stopped" list under current patterns
```

## Manual reminders (not automated)

When `travel-mode on` runs it prints these as a checklist — they need to be done in dashboards the script can't touch:

- **Plex remote stream quality cap** — Plex web → Settings → Network → Remote Streaming Quality. Cap at 4 Mbps so transcodes fit hotel bandwidth.
- **Tailscale exit node** — On Mac, switch to Forge as exit node if it's been activated (Phase 0.1 of the [Travel Mode plan](https://www.notion.so/352bb54b0db681d18b54f9d0d835ed9e)). This routes outbound traffic through GCP, useful when hotel networks block Tailscale UDP.

## Cross-references

- Phase 3 of the [Travel Mode plan](https://www.notion.so/352bb54b0db681d18b54f9d0d835ed9e) — this script is the implementation
- Companion to [`../caddy/`](../caddy/) (gateway) and [`../cloudflare/`](../cloudflare/) (DNS + tunnel) for the full travel-resilience stack
- Memory rule: heavy workloads during streaming starve Plex throughput — captured from prior incidents where Kometa at 5 rps caused SHIELD playback failures
