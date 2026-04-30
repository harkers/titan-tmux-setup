# ErsatzTV on titan

Creates 24/7 themed linear channels (Pluto-TV style) from the existing VOD library. Plex and Jellyfin can subscribe as M3U + XMLTV.

## Files
- `docker-compose.yml` — ErsatzTV container
- `config/` — channel definitions, schedules, EPG
- `backups/` — periodic config snapshots

## Common tasks
```bash
docker compose ps
docker compose logs -f
docker compose restart
```

## Cross-references
- `../iptv-blender/` — feeds VOD into linear channels
- `../jellyfin/` — secondary consumer
