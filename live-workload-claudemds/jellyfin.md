# Jellyfin on titan

Runs alongside Plex to test STRM/IPTV behaviour without disturbing the production Plex setup. Sandbox for investigating media-server issues or trying features before committing in Plex.

## Files
- `docker-compose.yml` — Jellyfin + Jellyseerr containers
- `config/` — Jellyfin server config
- `cache/` — transcoding cache (large, ~tens of GB)
- `jellyseerr-config/` — request UI

## Common tasks
```bash
docker compose ps
docker compose logs -f jellyfin
docker compose logs -f jellyseerr
```

## Web UIs (tailnet-only)
- Jellyfin: http://192.168.10.80:8096
- Jellyseerr: http://192.168.10.80:5055

## Cross-references
- `../plex/` — production sibling
- `../iptv-blender/` — shared VOD source
