# Kometa on titan

Plex collection + overlay manager. Heavy I/O — runs nightly at 03:00. Memory rule: never run during user TV time, hammers Plex at 5 rps and starves SHIELD playback.

## Files (live config — not all version-controlled)
- `config/` — main YAML configuration
- `config.bak-*` — automated config snapshots
- `docker-compose.yml` — runtime
- `*.json` — UK-focus award lists (BAFTA, BIFA, etc.)
- `force_match_*.py` — one-off helpers for problem ratingKeys
- `first-run.log` — most recent run log

## Common tasks
```bash
docker compose ps
docker logs -f kometa-collections | tail -100
docker compose run --rm kometa python kometa.py --collections-only
```

## Memory captures
- All pmm defaults re-enabled 2026-04-26
- Trakt re-auth flow documented in Notion
- `asset_folders: false` to use single-folder asset layout
- `imdb_search` migrated to `imdb_award` per upstream deprecation
- `radarr_add_missing` interactions can produce poisoned ratingKeys via PlexNotify webhook

## Cross-references
- `../plex-overlay/` — Python tool that replaces Kometa overlays at speed
- `../posterizarr/` — base poster source for both Kometa and plex-overlay
- `../cron/` — scheduling
