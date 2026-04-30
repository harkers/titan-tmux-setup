# titan project map

This file lives at `/home/stu/projects/CLAUDE.md` on titan. Claude Code walks up the directory tree finding `CLAUDE.md` files, so any session started in any subfolder gets this map loaded in addition to the per-folder context.

## Folder layout

| Folder | Size | Purpose | Per-folder context |
|---|---|---|---|
| `caddy/` | 28K | Reverse proxy for `*.harker.systems` | [`caddy/CLAUDE.md`](caddy/CLAUDE.md) |
| `cloudflare/` | 92K | CF API scripts (add/list/remove `*.harker.systems` services) | [`cloudflare/CLAUDE.md`](cloudflare/CLAUDE.md) |
| `claude/` | new | Versioned `~/.claude/` slice — status line + slash commands | [`claude/CLAUDE.md`](claude/CLAUDE.md) |
| `british-cinema/` | 32K | Deploy + status helpers for the static catalogue site | [`british-cinema/CLAUDE.md`](british-cinema/CLAUDE.md) |
| `travel-mode/` | 12K | `travel-mode on/off/status` bandwidth saver | [`travel-mode/CLAUDE.md`](travel-mode/CLAUDE.md) |
| `cron/` | 12K | `/etc/cron.d/*` snapshot + scheduling rule | [`cron/CLAUDE.md`](cron/CLAUDE.md) |
| `tmux/` | 16K | tmux config + `start-all-sessions.sh` | [`tmux/CLAUDE.md`](tmux/CLAUDE.md) |
| `vnc/` | 20K | TigerVNC + XFCE service files | [`vnc/CLAUDE.md`](vnc/CLAUDE.md) |
| `posterizarr/` | 2.4G | Plex DB recovery + Posterizarr container | [`posterizarr/CLAUDE.md`](posterizarr/CLAUDE.md) |
| `plex/` | 163G | Plex Media Server runtime | [`plex/CLAUDE.md`](plex/CLAUDE.md) |
| `plex-overlay/` | 94M | Pure-Python bulk overlay tool (replaces Kometa overlays) | [`plex-overlay/CLAUDE.md`](plex-overlay/CLAUDE.md) |
| `plex-ramdisk/` | 652K | tmpfs ramdisk for Plex hot data | [`plex-ramdisk/CLAUDE.md`](plex-ramdisk/CLAUDE.md) |
| `plex-tools/` | 384K | Python utilities for Plex library management | [`plex-tools/CLAUDE.md`](plex-tools/CLAUDE.md) |
| `kometa/` | 8.8G | Kometa runtime + posters/ build pipeline (feeds british-cinema) | [`kometa/CLAUDE.md`](kometa/CLAUDE.md) |
| `jellyfin/` | 83G | Jellyfin alongside Plex (sandbox) | [`jellyfin/CLAUDE.md`](jellyfin/CLAUDE.md) |
| `ersatztv/` | 24K | 24/7 linear channels from VOD (Pluto-TV style) | [`ersatztv/CLAUDE.md`](ersatztv/CLAUDE.md) |
| `iptv-blender/` | 138M | Blends IPTV VOD into Plex libraries | [`iptv-blender/CLAUDE.md`](iptv-blender/CLAUDE.md) |
| `iptv-blender-dryrun/` | 24K | Test variant of iptv-blender | — |
| `m3u-editor/` | 11G | M3U playlist editor (Laravel) | (project owns its own CLAUDE.md, 335 lines) |
| `media-stack/` | 117M | Media-related container stack | — |
| `epg/` (symlink) | — | XMLTV EPG server | [`epg/CLAUDE.md`](../epg/CLAUDE.md) |
| `OrderedEDGE/` | 452M | Local OE artefacts (system of record is on Mac) | — |
| `shield-apks/` | 214M | nVidia SHIELD APK backups | — |
| `pd-bulk/` | — | (legacy session, not a project folder) | — |

## Daily-driver shortcuts

```bash
tmux a -t plex                              # most-attached session
tmux ls                                      # see all 22 sessions
bash /home/stu/projects/tmux/start-all-sessions.sh  # rebuild any missing sessions

travel-mode on / off / status                # bandwidth saver
cd /home/stu/projects/cloudflare && python3 list_services.py   # tunnel routing
cd /home/stu/projects/british-cinema && ./status.sh             # cinema site state
```

Slash commands available in any Claude Code session here: `/homelab-status`, `/cf-list`, `/cf-add`, `/deploy-cinema`, `/travel-on`, `/travel-off`. See `claude/commands/README.md`.

## Shared conventions

- **UK quiet hours (03:00–06:00)** for heavy cron jobs — Kometa, Posterizarr, plex-overlay sync. Don't add anything that hammers Plex during likely viewing hours.
- **`tailscale serve` on titan** routes `/` → OpenClaw `:18789` and `/british-cinema/` → `/var/www/british-cinema`. Adding paths is fine; replacing the binding wholesale knocks out OpenClaw.
- **`*.harker.systems` reverse proxy** lives in Caddy, gated by Cloudflare Access at the tunnel ingress. Don't add direct LAN-only services to Caddy; use direct IP:port + Tailscale.
- **The `harker.systems` tunnel (`8ba2b285…`) is healthy** and the active homelab tunnel. `titan-home` (`18a78b3b…`) is degraded and only routes a few subdomains.

## Cross-references

- Repo: [github.com/harkers/titan-tmux-setup](https://github.com/harkers/titan-tmux-setup)
- Notion: [Travel Mode plan](https://www.notion.so/352bb54b0db681d18b54f9d0d835ed9e), [Implementation Log](https://www.notion.so/352bb54b0db681038fd2d217846fd510), [British Cinema](https://www.notion.so/352bb54b0db6815ea748f83ae7d3257a)
