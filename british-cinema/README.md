# British Cinema — static catalogue site

A 1409-collection map of British and world cinema as catalogued by [harkers/kometa-config](https://github.com/harkers/kometa-config). Generated from TMDB + Trakt sources, illustrated with custom posters, and served at:

- [https://titan.tail1a2109.ts.net/british-cinema/](https://titan.tail1a2109.ts.net/british-cinema/) (tailnet only)

## Stack

```
/home/stu/projects/kometa/posters/        ← build pipeline (Python)
        │
        │  build_site.py reads data/*.json + assets/
        ▼
/home/stu/projects/kometa/posters/site/   ← staging output (~352M)
        │
        │  deploy.sh rsync's
        ▼
/var/www/british-cinema/                  ← deployed copy
        │
        │  tailscale serve --bg
        ▼
https://titan.tail1a2109.ts.net/british-cinema/
```

The build pipeline lives under `kometa/posters/` because it shares data + assets with Kometa's own poster generation. This `british-cinema/` project folder is the **deployment + serving** concern — it knows about `/var/www/british-cinema/` and the `tailscale serve` config, not about the build internals.

## Sections (counts as of 2026-04-30)

| Section | Pages | URL |
|---|---|---|
| Actors | 852 | [/british-cinema/actors/](https://titan.tail1a2109.ts.net/british-cinema/actors/) |
| Themes | 207 | [/british-cinema/themes/](https://titan.tail1a2109.ts.net/british-cinema/themes/) |
| Directors | 172 | [/british-cinema/directors/](https://titan.tail1a2109.ts.net/british-cinema/directors/) |
| Awards | 74 | [/british-cinema/awards/](https://titan.tail1a2109.ts.net/british-cinema/awards/) |
| TV | 69 | [/british-cinema/tv/](https://titan.tail1a2109.ts.net/british-cinema/tv/) |
| Studios | 41 | [/british-cinema/studios/](https://titan.tail1a2109.ts.net/british-cinema/studios/) |

Total: 1,415 pages, 352 MB on disk. Run `./status.sh` for the live numbers.

## Files in this folder

| File | Purpose |
|---|---|
| `deploy.sh` | rebuild from kometa/posters + rsync to /var/www/british-cinema |
| `status.sh` | show tailscale serve config + last deploy time |
| `README.md` | this |
| `CLAUDE.md` | context for future Claude Code sessions |

## Update + redeploy

```bash
cd /home/stu/projects/british-cinema
./deploy.sh
```

This wraps the canonical build (`build_site.py`) and the rsync into a single command. Nothing here mutates the build scripts — those stay in `kometa/posters/`.

## How serving works

Static files come from `/var/www/british-cinema/` via `tailscale serve` configured for path-based routing:

```
tailscale serve --bg --set-path /british-cinema /var/www/british-cinema
```

The same Tailscale Funnel binding also fronts other paths (`/` proxies to OpenClaw at `127.0.0.1:18789`). Don't replace the binding wholesale — only add/remove specific paths.

## Cross-references

- Build pipeline: [`/home/stu/projects/kometa/posters/build_site.py`](file:///home/stu/projects/kometa/posters/build_site.py)
- Source data: `kometa/posters/data/all.json` + `bios.json` + `tmdb_map.json`
- Memory: [British actor collections build 2026-04-27](file:///Users/stu/.claude/projects/-Users-stu-plex/memory/) — 800 actor collections, era-themed SDXL posters, Wikipedia + TMDB bios
- Memory: [British Cinema static site](file:///Users/stu/.claude/projects/-Users-stu-plex/memory/) — site reference (this one)
