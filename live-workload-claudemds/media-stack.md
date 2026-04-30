# media-stack on titan

Container stack for various media-related tooling. Sparse folder — most logic lives in `docker-compose.yml`.

## Files
- `docker-compose.yml` — current stack
- `docker-compose.yml.bak.*` — historical snapshots
- `config/`

## Common tasks
```bash
docker compose ps
docker compose logs --tail 50
docker compose pull && docker compose up -d
```

## Note
Inspect `docker-compose.yml` to see what's currently in scope — this stack changes often as adjacent projects (plex, kometa, plex-overlay) absorb pieces.
