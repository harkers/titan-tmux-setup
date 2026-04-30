# travel-mode on titan

Bandwidth saver. Pauses chatty AI/agent containers + heavy Plex maintenance crons for the duration of a trip. Lives at `/home/stu/projects/travel-mode/`, symlinked to `/home/stu/bin/travel-mode`.

## Usage

```bash
travel-mode status     # what's currently paused, what would match
travel-mode on         # the morning you fly
travel-mode off        # when home
```

State lives in `~/.travel-mode/`:
- `paused-containers.txt` — written by `on`, read by `off`
- `crontab.bak` — full snapshot before `on`
- `travel-mode.log` — append-only audit trail

## What gets paused

Container regex (in the script's `PAUSE_CONTAINER_PATTERNS` array):
- `^ollama` — local LLM serving
- `^kometa-` — Kometa runtime
- `^openclaw-.*-(agent|deployer|sbx|embedding|docling|selenium|powerpoint)` — heavy MCP workloads
- `^openclaw-.*-mcp$` — chatty MCP servers (talk to external APIs)

Cron substring (case-insensitive):
- `kometa`, `posterizarr-cycle`, `plex-overlay-sync`, `tmdb-enrich`

## What stays running

User-facing media (Plex, Posterizarr, Jellyfin, ErsatzTV), user-facing services (OpenClaw Nextcloud, Nitter, Pi-hole), data stores (Redis, Qdrant, Vault, MariaDB, PostgreSQL), infrastructure (Caddy, cloudflared, all `*-gateway` containers).

## Gotchas

- **Refuses double-on** — if `paused-containers.txt` exists with content, run `off` first to avoid losing track of what should be restarted.
- **Manual reminders printed at end of `on`** for things the script can't touch: Plex web UI quality cap, Tailscale exit-node switch.

## Cross-references

- [Phase 3 of Travel Mode plan](https://www.notion.so/352bb54b0db681d18b54f9d0d835ed9e) — this is the implementation
- [`../caddy/CLAUDE.md`](../caddy/CLAUDE.md) and [`../cloudflare/CLAUDE.md`](../cloudflare/CLAUDE.md) — companion gateway + DNS layer
- [memory: don't run kometa during user TV time](../../memory) — generalised here for remote streaming
