# Posterizarr + Plex DB recovery on titan

Posterizarr is a PowerShell-based bulk poster generator that runs in Docker on titan. The two scripts here cover its known failure modes. Lives at `/home/stu/projects/posterizarr/`.

## Files

- `docker-compose.yml` — Posterizarr container at port 8000
- `cycle.sh` — restart Plex+Posterizarr if Posterizarr's log goes silent >5 min
- `repair_plex_xml.sh` — strip `ma:channels` poison from Plex SQLite (busy_timeout=30000, no Plex stop required)

## Failure modes (and the cron entries that handle them)

### Posterizarr hang
Container alive, Posterizarr's log frozen, no progress. Cron `posterizarr-cycle` runs `cycle.sh` every 4h — detects the silent log and restarts both Posterizarr and Plex.

### Plex DB poison
MediaAnalysis writes `ma:channels` keys into `extra_data` of certain media rows. After a few days some rows get `ma:channels` *appended* causing duplicate-channels XML corruption that breaks Plex's library walk. Cron `plex-xml-repair` runs `repair_plex_xml.sh` every 2h — strips the keys via SQL UPDATE without stopping Plex.

## Common tasks

```bash
# trigger cycle.sh manually
bash /home/stu/projects/posterizarr/cycle.sh

# trigger XML repair manually
bash /home/stu/projects/posterizarr/repair_plex_xml.sh

# tail logs
docker logs -f posterizarr | tail -100
tail -f ~/projects/posterizarr/cycle.log 2>/dev/null
```

## Live config (NOT in git)

Posterizarr's `config.json` has TMDb v4 token + Fanart API key + Plex token. Don't commit it. The compose volume mount keeps it at `~/projects/posterizarr/config/config.json` on titan.

## Gotchas

- TMDb config uses **v4 JWT token** not v3 API key. Memory: I once put a v3 key in there and Posterizarr silently rejected requests.
- Posterizarr first-run takes 3–5 days for a 15K library at the rate it can write Plex posters. Don't restart unless cycle.sh has triggered.

## Cross-references

- [`../cron/CLAUDE.md`](../cron/CLAUDE.md) — cadence rationale
- [`../../plex-overlay/`](../../plex-overlay/) on titan — once Posterizarr first-run finishes, plex-overlay can use Posterizarr's outputs as base posters
