# Cron entries on titan

Documentation for `/etc/cron.d/*` — not the cron files themselves. Lives at `/home/stu/projects/cron/`.

## Active entries (snapshot 2026-04-30)

| File | Cadence | What it does |
|---|---|---|
| `posterizarr-cycle` | every 4h | runs `cycle.sh` — restarts Plex+Posterizarr if log silent >5 min |
| `plex-xml-repair` | every 2h | strips `ma:channels` poison from Plex SQLite, no Plex stop |
| `plex-overlay-sync-ribbons` | Sun 03:00 | refreshes IMDb Top 250 + Oscar labels |
| `kometa` | nightly 03:00 | Kometa overlay phase, heavy I/O |

User crontab also has heavy entries: `bulk-populate.sh` every 5 min, EPG merges every 15 min, `tmdb-enrich` daily.

## Scheduling rule (hard, from past incidents)

**Heavy jobs go in UK 03:00–06:00 quiet hours.** Memory note: Kometa at 5 rps starves SHIELD's Plex throughput within minutes — never schedule it during likely viewing time. The `travel-mode` script ([../travel-mode/](../travel-mode/)) pauses these heavy crons explicitly when on.

## Common tasks

```bash
# show user crontab
crontab -l

# show /etc/cron.d/* (all system jobs)
sudo ls /etc/cron.d/

# tail a job's log
tail -f /home/stu/epg/epg-update.log
tail -f /home/stu/projects/plex/bulk.log

# audit before a trip
crontab -l && sudo ls /etc/cron.d/
```

## Cross-references

- [`../travel-mode/CLAUDE.md`](../travel-mode/CLAUDE.md) — what gets paused on `travel-mode on`
- [`../posterizarr/CLAUDE.md`](../posterizarr/CLAUDE.md) — explains the cycle.sh + repair_plex_xml.sh failure modes
- [memory: don't run kometa during user TV time](../../memory)
