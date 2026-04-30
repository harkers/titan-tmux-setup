# Plex Media Server on titan

The main Plex Media Server runtime. Largest folder in /home/stu/projects/ at ~163G.

## Files
- `docker-compose.yml` — Plex container (port 32400)
- `config/` — Plex DB, libraries, playlists, transcoder cache
- `attic/` — historical artefacts
- `bulk-populate.sh` / `bulk-populate-tv.sh` — feed Plex from tmdb/imdb metadata caches
- `bulk-populate.sql` / `bulk-populate-tv.sql` — SQL these scripts use
- `recordings/` — DVR captures

## Cron entries
- `bulk-populate.sh` every 5 min (movies)
- `bulk-populate-tv.sh` every 5 min (TV)
- `tmdb-enrich.sh` daily 04:00
- `tmdb-enrich-tv.sh` daily 04:15

These are paused by `travel-mode on`.

## Memory captures (from incidents)
- secureConnections enum: 0=Required, 1=Preferred, 2=Disabled (UI hides Disabled, only API can set)
- Auto-scans + Radarr PlexNotify webhook = poisoned ratingKeys; both disabled, 02:00 cron sweeps imports
- MediaAnalysis writes ma:channels poison; `repair_plex_xml.sh` runs every 2h to strip
- Plex hangs after sustained pressure (TCP accepts but no HTTP); `cycle.sh` restarts on log silence >5min
- SHIELD at 192.168.10.128 needs split-tunnel for NordVPN to not hijack DNS
- Reach via plex.harker.systems through wildcard A record `80.5.36.105`, NOT through any tunnel

## Cross-references
- `../posterizarr/` — Plex DB recovery scripts
- `../plex-ramdisk/` — tmpfs config for hot media
- `../plex-overlay/` — overlay layer
- `../kometa/` — collection layer
