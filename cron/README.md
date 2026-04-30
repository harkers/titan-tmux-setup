# Cron entries

Every `/etc/cron.d/*` file that keeps the homelab healthy on titan. Snapshotted into [`all-cron-entries.txt`](all-cron-entries.txt) — review and copy what you need before installing.

## Active entries

| File | Cadence | What it does |
|---|---|---|
| `posterizarr-cycle` | every 4h | runs `cycle.sh` — restarts Plex + Posterizarr if Posterizarr's log went silent for >5 min (covers the "container alive but hung" failure) |
| `plex-xml-repair` | every 2h | runs `repair_plex_xml.sh` — strips `ma:channels` poison from Plex SQLite using `busy_timeout=30000`, no Plex stop required |
| `plex-overlay-sync-ribbons` | Sundays 03:00 | refreshes IMDb Top 250 + Oscar winner labels on Plex, drives plex-overlay's ribbon decisions |
| `kometa` | nightly 03:00 | runs Kometa overlay phase (heavy — keep in UK quiet hours) |

See [`../posterizarr/README.md`](../posterizarr/README.md) for the cycle/repair scripts and what triggers each failure mode.

## Install on a fresh titan

```bash
# Adjust paths inside `all-cron-entries.txt` first, then:
sudo cp all-cron-entries.txt /etc/cron.d/titan-homelab
sudo chmod 644 /etc/cron.d/titan-homelab
sudo systemctl restart cron
```

If the file mixes multiple discrete jobs, prefer splitting it into one file per job (`/etc/cron.d/posterizarr-cycle`, `/etc/cron.d/plex-xml-repair`, etc.) so individual cadences are easier to find later.

## Audit before travel

Before flying, run `crontab -l` for both your user account and root, plus `ls /etc/cron.d/` — make sure nothing's been added by a one-shot script that you forgot about. The Phase 3 `travel-mode on` script in the [Notion plan](https://www.notion.so/352bb54b0db681d18b54f9d0d835ed9e) backs up the current crontab before pausing entries.

## Schedule philosophy

All heavy jobs (Kometa, posterizarr, plex-overlay sync) live in **UK 03:00–06:00** quiet hours so they don't compete with evening streaming traffic. Memory rule from prior incidents: Kometa at 5 rps starves SHIELD's Plex throughput within minutes, so never schedule it during likely viewing time.
