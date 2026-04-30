# Cloudflare management for harker.systems

Idempotent Python scripts for managing the `harker.systems` Cloudflare zone, tunnel ingress, and Access apps. Built during the Phase 1 + 5.B rollout on 2026-04-30 — see [Notion plan](https://www.notion.so/352bb54b0db681d18b54f9d0d835ed9e).

All scripts share `cf_common.py` (token loader, IDs, API helpers) and use the standard library only — no `pip install` step.

## Layout

| File | Purpose |
|---|---|
| `cf_common.py` | Shared helpers: token loader, IDs, `cf()` request wrapper |
| `add_service.py` | Add one service: CNAME + tunnel ingress (optional auth) |
| `list_services.py` | Show all hostnames routed by the harker.systems tunnel |
| `remove_service.py` | Delete a service: drops CNAME and tunnel ingress |
| `.env.example` | Template for the API credentials |

The historical bulk-import scripts that did the original 34-service rollout, audTag expansion, and Access app creation live in `bootstrap/` — kept for reference but already applied.

## Setup on titan

```bash
# one-time, on titan
mkdir -p /home/stu/projects/cloudflare
cd /home/stu/projects/cloudflare
# clone or rsync this folder, then:
cp .env.example .env
chmod 600 .env
# paste CF_API_TOKEN + CF_ACCOUNT_ID into .env
```

## Setup on macbook

The scripts auto-detect `/Users/stu/Projects/ordered-edge/.env.secrets` if no other `.env` is present. No additional step needed.

## Common tasks

### Add a new service

```bash
# Behind CF Access (default)
python3 add_service.py grafana
python3 add_service.py wazuh

# Public bypass (guest access, owns its own auth)
python3 add_service.py overseerr --bypass
python3 add_service.py audiobookshelf --bypass
```

After adding the CF side, also add a site block to [`../caddy/Caddyfile`](../caddy/Caddyfile) and reload:

```bash
docker exec caddy caddy reload --config /etc/caddy/Caddyfile
```

### List the live routing table

```bash
python3 list_services.py
```

### Remove a service

```bash
python3 remove_service.py grafana
```

Then drop the corresponding site block from the Caddyfile.

## What's already deployed

(Captured 2026-04-30, listing only `*.harker.systems` rules — `*.rker.dev` and `*.teamharker.com` rules on the same tunnel are untouched.)

| Hostname | Auth | Backend |
|---|---|---|
| `posterizarr` `dozzle` `pihole` `nextcloud` `forge` `ollama` `iptv` `epg` `atlas` | gated | titan-local via Caddy |
| `radarr` `sonarr` `lidarr` `readarr` `prowlarr` `bazarr` `lazylibrarian` `tautulli` `qbittorrent` `nzbget` `portainer` | gated | zeus servarr CT 105 via Caddy |
| `copilot` `wazuh` `graylog` `grafana` | gated | zeus SIEM CT 103 via Caddy |
| `searxng` `spiderfoot` `nessus` | gated | zeus OSINT CT 201 via Caddy |
| `gitea` `cosmos` `omada` `proxmox` | gated | zeus infra via Caddy |
| `jellyseerr` `nitter` | bypass | titan-local via Caddy |
| `overseerr` | bypass | zeus servarr CT 105 via Caddy |
| `ssh` | gated | titan SSH (port 22) — Phase 5.B break-glass |
| `titan` `vault` `budget` `ab` | (existing, untouched) | direct to LAN backends |

Run `list_services.py` for the live state.

## Architecture

```
Internet
  │
  ▼
Cloudflare Access (auth at edge)        ◀── Apps: "Harker Systems Homelab" (*.harker.systems)
  │                                          and "Dashboard" (*.teamharker.com)
  ▼
Cloudflare Tunnel "harker.systems"      ◀── id 8ba2b285-...
  (cloudflared on cosmos CT 115)
  │
  ├─→ direct to LAN backends (existing rules: nas / git.rker.dev / cloud / haos / titan / etc.)
  │
  └─→ http://192.168.10.80:80 ──► Caddy on titan ──► fan-out by Host header
                                                  ├─→ 127.0.0.1:* (titan-local)
                                                  └─→ 192.168.10.x:* (zeus services)
```

## Token scopes

Whichever token is in your `.env`/`.env.secrets` must have:

- **Zone · DNS · Edit** on the `harker.systems` zone (for CNAMEs)
- **Account · Cloudflare Tunnel · Edit** (for tunnel ingress updates)
- **Account · Access: Apps and Policies · Edit** (only needed if creating new Access apps)

The scripts here don't currently need PATCH on existing Access apps. If you re-issue the token, generate it from [the API tokens page](https://dash.cloudflare.com/profile/api-tokens) and paste into `.env`.

## Cross-references

- [Caddyfile that consumes these rules](../caddy/Caddyfile)
- [Travel-mode plan in Notion](https://www.notion.so/352bb54b0db681d18b54f9d0d835ed9e)
- [Forge Zero Trust setup (the Clavis pattern this mirrors)](https://www.notion.so/338bb54b0db6814f8e30c209f90f3266)
