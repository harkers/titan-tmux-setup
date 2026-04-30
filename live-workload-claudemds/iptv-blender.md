# iptv-blender

Blends IPTV VOD catalogue into Plex main libraries. Python project, Docker-deployable.

## Files
- `docker-compose.example.yml` — runtime template
- `pyproject.toml` — Python deps
- `src/` — application code
- `scripts/` — operational helpers
- `state/` — runtime state (don't commit)
- `tests/`
- `docs/superpowers/specs/2026-04-20-iptv-plex-blend-architecture-design.md` — design

## Common tasks
```bash
ls state/
docker compose up -d
pytest
```

## Cross-references
- `../iptv-blender-dryrun/` — staging variant
- `../plex/` — primary consumer
- `../m3u-editor/` — upstream IPTV playlist source
