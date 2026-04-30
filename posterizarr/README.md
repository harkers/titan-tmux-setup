# Posterizarr on titan

[Posterizarr](https://github.com/fscorrupt/Posterizarr) builds branded base posters from TMDb / Fanart.tv / TVDB / Plex art. Drops them into a Kometa-compatible asset tree at `/home/stu/projects/posterizarr/assets/Movies/<Title> (<Year>)/poster.jpg`.

Then [`plex-overlay`](https://github.com/harkers/plex-overlay) reads those assets as the second-tier fallback for its own overlay run — branded base + metadata badges in two stages.

## Install

1. Make directories:
   ```bash
   mkdir -p /home/stu/projects/posterizarr/{config,assets,assetsbackup,manualassets,watcher}
   ```
2. Copy `docker-compose.yml` from this repo into `/home/stu/projects/posterizarr/`.
3. Pull image + start:
   ```bash
   cd /home/stu/projects/posterizarr
   docker compose pull && docker compose up -d
   ```
4. Posterizarr generates a `config.json` template on first run. Edit `config/config.json`:
   - `ApiPart.tmdbtoken` → TMDb v4 Read Access Token (NOT v3 API key — Posterizarr enforces v4)
   - `ApiPart.FanartTvAPIKey` → Fanart.tv API key
   - `ApiPart.PlexToken` → Plex token
   - `PlexPart.LibstoExclude` → list of library names to skip (we use `["IPTV Movies", "IPTV Series", "Wrestling"]`)
   - `PlexPart.UsePlex` → `"true"`
5. Trigger a run:
   ```bash
   docker exec -d posterizarr pwsh /app/Posterizarr.ps1
   ```

## Web UI

`http://titan.tail1a2109.ts.net:8000`

## Files in this directory

| File | Purpose |
|---|---|
| [`docker-compose.yml`](docker-compose.yml) | Container definition — `host` network, volume mounts, RUN_TIME=23:00 daily |
| [`cycle.sh`](cycle.sh) | Recovers Posterizarr+Plex when they hang. Runs every 4h via cron. |
| [`repair_plex_xml.sh`](repair_plex_xml.sh) | Strips `ma:channels` JSON keys that Plex's MediaAnalysis re-adds and that breaks every strict-XML consumer (Posterizarr, Kometa, plex-overlay). Runs every 2h via cron. |

## Known issues + workarounds

### 1. Plex HTTP listener hangs after sustained API pressure

Symptom: `curl http://localhost:32400/identity` returns empty body / timeout. Container shows "Up X hours (unhealthy)". Posterizarr stuck on a single item for hours.

Workaround: [`cycle.sh`](cycle.sh) detects this (Posterizarr log inactivity > 5 min) and restarts Plex + Posterizarr automatically every 4h.

### 2. Plex MediaAnalysis re-poisons DB with duplicate `channels` attribute

Symptom: per-item Plex XML has `channels="6" ... channels="6"` on a `<Stream>` element. .NET XmlDocument (Posterizarr) and other strict parsers reject as malformed. About 6-15 movies affected per day.

Root cause: Plex's serializer reads both the native `media_streams.channels` column AND a `ma:channels` key in the row's `extra_data` JSON, and unprefixes the second one to `channels=` without dedup. MediaAnalysis re-adds `ma:channels` periodically.

Workaround: [`repair_plex_xml.sh`](repair_plex_xml.sh) removes `ma:channels` and `ma:bitRate` JSON keys from poisoned rows. Uses `busy_timeout = 30000` to update without stopping Plex (SQLite WAL-mode allows concurrent writers when reader has finished its read transaction). Runs every 2h via cron.

Diagnosis confirmed via deep QA — see this repo's git history for the analysis.

## Operating

```bash
# Logs
docker logs posterizarr -f
tail -F /home/stu/projects/posterizarr/cycle.log
tail -F /home/stu/projects/posterizarr/repair_plex_xml.log

# Force a manual run
docker exec posterizarr rm -f /config/temp/Posterizarr.Running
docker exec -d posterizarr pwsh /app/Posterizarr.ps1

# Stop the world
docker compose down

# Asset count
find /home/stu/projects/posterizarr/assets -type f | wc -l
```

## Approximate timing

- Library walk: ~80 min for 15K movies
- Per-poster processing: ~1-2 sec for cached, up to 30+ sec when source needs negotiating across TMDb + Fanart.tv + TVDB + Plex
- Sustained throughput with cycle restarts handling Plex hangs: ~150-200 posters/hour
- Full library: **~3-5 days** unattended
