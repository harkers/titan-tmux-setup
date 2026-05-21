# tmux-setup

Homelab config + setup notes for `titan` (Debian 12 server, 64 GB RAM, 16 core).

What lives where on titan:
- **Plex Media Server** in Docker (`/home/stu/projects/plex/`)
- **Kometa** (Plex Meta Manager) in Docker (`/home/stu/projects/kometa/`)
- **plex-overlay** — bulk overlay tool, see [github.com/harkers/plex-overlay](https://github.com/harkers/plex-overlay) (when pushed)
- **Posterizarr** — base poster builder in Docker (`/home/stu/projects/posterizarr/`)
- **NZBGet** — on zeus CT 105, not titan
- **Radarr** — on zeus 192.168.10.29:7878

## Layout of this repo

| Dir | Contents |
|---|---|
| [`tmux/`](tmux/) | `~/.tmux.conf` for sane defaults + persistent sessions |
| [`vnc/`](vnc/) | TigerVNC + XFCE remote desktop on `:1` (port 5901) |
| [`caddy/`](caddy/) | Reverse proxy for `*.harker.systems` — fronted by Cloudflare Access |
| [`cloudflare/`](cloudflare/) | API scripts to add/list/remove `*.harker.systems` services + bootstrap history |
| [`claude/`](claude/) | Claude Code status-line script + setup snippet (the versioned slice of `~/.claude/`) |
| [`british-cinema/`](british-cinema/) | Deploy + serve helpers for the static catalogue at titan.tail1a2109.ts.net/british-cinema/ |
| [`travel-mode/`](travel-mode/) | `travel-mode on/off/status` bandwidth saver for trips |
| [`posterizarr/`](posterizarr/) | docker-compose, auto-recovery cycle script, Plex DB poison-repair script |
| [`cron/`](cron/) | All `/etc/cron.d/` entries that keep the homelab healthy |

Each folder has its own `README.md` and is structured as a self-contained project that can be rsync'd to `/home/stu/projects/<name>/` on titan.

## Quick recovery / new-machine bootstrap

```bash
# Clone next to where projects will live
git clone https://github.com/harkers/tmux-setup.git ~/tmux-setup
mkdir -p ~/projects ~/bin

# Each folder rsyncs into its target on titan, preserving live state.
for d in caddy cloudflare claude cron tmux vnc travel-mode british-cinema; do
  rsync -a "~/tmux-setup/$d/" "~/projects/$d/"
done

# tmux conf
cp ~/projects/tmux/.tmux.conf ~/

# Spin up one detached tmux session per project folder
bash ~/projects/tmux/start-all-sessions.sh

# travel-mode bin symlink
ln -sfn ~/projects/travel-mode/travel-mode.sh ~/bin/travel-mode

# Caddy (after Docker)
cd ~/projects/caddy && docker compose up -d

# Cloudflare scripts: drop the API token into ~/projects/cloudflare/.env (chmod 600)
# (see cloudflare/README.md for the required scopes)

# Claude Code status line + slash commands
ln -sfn ~/projects/claude/statusline-command.sh ~/.claude/statusline-command.sh
mkdir -p ~/.claude/commands
for f in ~/projects/claude/commands/*.md; do
  [ "$(basename $f)" = "README.md" ] && continue
  ln -sfn "$f" "$HOME/.claude/commands/$(basename $f)"
done
# Then merge the statusLine block from claude/settings.example.json into ~/.claude/settings.json

# VNC (after apt install xfce4 tigervnc-standalone-server tightvncpasswd)
mkdir -p ~/.vnc ~/.config/systemd/user
cp ~/projects/vnc/{xstartup,config} ~/.vnc/
cp ~/projects/vnc/vncserver.service ~/.config/systemd/user/
echo -e 'PASSWORD\nPASSWORD\nn' | tightvncpasswd -f > ~/.vnc/passwd
chmod 600 ~/.vnc/passwd
sudo loginctl enable-linger $USER
systemctl --user enable --now vncserver.service

# Posterizarr (after Docker + image pulled)
mkdir -p ~/projects/posterizarr/{config,assets,assetsbackup,manualassets,watcher}
chmod +x ~/projects/posterizarr/{cycle.sh,repair_plex_xml.sh}
# Edit config.json with TMDb v4 token, Fanart key, Plex token

# Cron
sudo cp ~/projects/cron/* /etc/cron.d/   # adjust paths first
```

## Services running on titan

Tailscale hostname `titan.tail1a2109.ts.net` resolves automatically when you're connected to the tailnet. LAN IP is `192.168.10.80`. Both work; tailscale is preferred from outside the LAN.

### Media stack

| Service | Port | URL | Notes |
|---|---|---|---|
| **Plex Media Server** | 32400 | [titan.tail1a2109.ts.net:32400/web](http://titan.tail1a2109.ts.net:32400/web) | Movies + TV + IPTV libraries |
| **Posterizarr** | 8000 | [titan.tail1a2109.ts.net:8000](http://titan.tail1a2109.ts.net:8000) | Base poster builder |
| **Jellyseerr** | 5055 | [titan.tail1a2109.ts.net:5055](http://titan.tail1a2109.ts.net:5055) | Media request UI |
| **Sonarr** | 8989 | [192.168.10.80:8989](http://192.168.10.80:8989) | TV automation (LAN-bound) |
| **Radarr (titan)** | 7878 | [192.168.10.80:7878](http://192.168.10.80:7878) | Movie automation (LAN-bound; the *real* Radarr is on zeus) |
| **Prowlarr** | 9696 | [192.168.10.80:9696](http://192.168.10.80:9696) | Indexer manager |
| **m3u-editor** | 36400-36401 | [192.168.10.80:36400](http://192.168.10.80:36400) | IPTV playlist editor |
| **iptv-blender** | 9110 | [titan.tail1a2109.ts.net:9110](http://titan.tail1a2109.ts.net:9110) | Custom IPTV merger |
| **EPG server** | 3000 | [titan.tail1a2109.ts.net:3000](http://titan.tail1a2109.ts.net:3000) | XMLTV electronic program guide |

### Infra & monitoring

| Service | Port | URL | Notes |
|---|---|---|---|
| **TigerVNC desktop** | 5901 | `vnc://titan.tail1a2109.ts.net:5901` | XFCE — see [vnc/README.md](vnc/README.md) |
| **Dozzle** | 8889 | [titan.tail1a2109.ts.net:8889](http://titan.tail1a2109.ts.net:8889) | Live Docker log viewer |
| **Pi-hole** | 8090 | [titan.tail1a2109.ts.net:8090/admin](http://titan.tail1a2109.ts.net:8090/admin) | DNS filtering |
| **Authentik** | 9000 | localhost only — SSH-tunnel `-L 9000:localhost:9000` | SSO / OAuth |
| **Vaultwarden** | 4743 | localhost only | Bitwarden-compat password vault |
| **Glances** | 61209 | localhost only — `glances -w` for browser | System metrics |
| **node_exporter** | 9100 | scraped by Prometheus | Host metrics |
| **promtail** | 39741 | feeds Loki | Log shipping |
| **iperf3** | 5201 | `iperf3 -c titan` from any tailnet peer | Network speed test |

### Personal projects

| Service | Port | URL | Notes |
|---|---|---|---|
| **Forge Pipeline** | 4174 | [titan.tail1a2109.ts.net:4174](http://titan.tail1a2109.ts.net:4174) | Build pipeline UI |
| **Privacy Ops Dashboard** | 3010 | [192.168.10.80:3010](http://192.168.10.80:3010) | Privacy-Ops product |
| **Privacy Ops Staging** | 3011 | [192.168.10.80:3011](http://192.168.10.80:3011) | Staging build |
| **OpenClaw Nextcloud** | 8083 | [titan.tail1a2109.ts.net:8083](http://titan.tail1a2109.ts.net:8083) | Self-hosted file sync |
| **Open WebUI** | 8080 | [titan.tail1a2109.ts.net:8080](http://titan.tail1a2109.ts.net:8080) | Ollama frontend |
| **Ollama API** | 11434 | localhost only — `curl http://localhost:11434/api/tags` | Local LLM serving |
| **Nitter** | 8060 | [titan.tail1a2109.ts.net:8060](http://titan.tail1a2109.ts.net:8060) | Twitter frontend |
| **Gradio app** | 7860 | [titan.tail1a2109.ts.net:7860](http://titan.tail1a2109.ts.net:7860) | ML demo UI |

### System

| Service | Port | Notes |
|---|---|---|
| SSH | 22, 2222 | `ssh titan` |
| SMB / CIFS | 139, 445 | Windows file sharing |
| NFS | 111, 2049 | Linux file sharing |
| MariaDB | 3306 | localhost-only; container DBs separate |
| PostgreSQL | 5432 | localhost-only |
| cloudflared | 20241 | Cloudflare tunnel daemon |

### Quick health probe

```bash
ssh titan 'for p in 32400 8000 5055 7878 8989 9696 8889 4174 3010 8083 9110 8090 5901; do
  printf "%-5s -> " "$p"
  curl -s --max-time 3 -o /dev/null -w "%{http_code}\n" http://localhost:$p/ 2>/dev/null
done'
```

### Updating this list

```bash
ssh titan "sudo ss -tnlp 2>/dev/null | grep LISTEN" | sort -t: -k2 -n
```

The listing above is captured **2026-04-30**. Re-run the command + update the README when ports change.

## Services running on zeus

`zeus` is the Proxmox VE 8.4 hypervisor at LAN `192.168.10.150` (tailscale `zeus.tail1a2109.ts.net` → `100.95.138.89`). It hosts ten LXC containers and three VMs. Every service listed below is reachable on the LAN by IP, and over Tailscale via `ssh -J zeus` style jumps once you're on the tailnet.

> Tailscale SSH on zeus requires `root` (no `stu` user inside Proxmox containers): `ssh root@zeus`.

### Proxmox host

| Service | URL | Notes |
|---|---|---|
| **Proxmox web UI** | [192.168.10.150:8006](https://192.168.10.150:8006) | The hypervisor — manage all CT/VMs from here |
| **Zeus dashboard** | [192.168.10.150](http://192.168.10.150) | Custom landing page |
| **pve-api-daemon** | port 3128 | Spice console proxy |
| SSH | 22 | `ssh root@zeus` (tailscale auth) or `ssh root@192.168.10.150` |

### CT 105 — `servarr` (192.168.10.29)

The main \*arr media-automation stack, mostly running through a `gluetun` VPN container.

| Service | Port | URL | Notes |
|---|---|---|---|
| **Radarr** | 7878 | [192.168.10.29:7878](http://192.168.10.29:7878) | Movie automation — the *real* Radarr, not titan's |
| **Sonarr** | 8989 | [192.168.10.29:8989](http://192.168.10.29:8989) | TV automation |
| **Lidarr** | 8686 | [192.168.10.29:8686](http://192.168.10.29:8686) | Music automation |
| **Readarr** | 8787 | [192.168.10.29:8787](http://192.168.10.29:8787) | Books / audiobooks automation |
| **Prowlarr** | 9696 | [192.168.10.29:9696](http://192.168.10.29:9696) | Indexer manager (via gluetun) |
| **Bazarr** | 6767 | [192.168.10.29:6767](http://192.168.10.29:6767) | Subtitle automation |
| **LazyLibrarian** | 5399 | [192.168.10.29:5399](http://192.168.10.29:5399) | Author/book tracker |
| **Overseerr** | 5055 | [192.168.10.29:5055](http://192.168.10.29:5055) | Media request UI (predecessor to titan's Jellyseerr) |
| **Tautulli** | 8181 | [192.168.10.29:8181](http://192.168.10.29:8181) | Plex stats / monitoring |
| **Audiobookshelf** | 13378 | [192.168.10.29:13378](http://192.168.10.29:13378) | Audiobook + podcast server |
| **qBittorrent** | 8080 | [192.168.10.29:8080](http://192.168.10.29:8080) | Torrent client (via gluetun) |
| **NZBGet** | 6789 | [192.168.10.29:6789](http://192.168.10.29:6789) | Usenet downloader (via gluetun) |
| **BitTorrent peer** | 6881 | n/a | Torrent peer port (via gluetun) |
| **Portainer** | 9443 | [192.168.10.29:9443](https://192.168.10.29:9443) | Docker UI (HTTPS) |
| **Portainer agent** | 8000 | n/a | Edge agent endpoint |
| **Kali NoVNC** | 9999 | [192.168.10.29:9999](http://192.168.10.29:9999) | Browser-based Kali Linux desktop |
| **PostgreSQL** | 5432 | n/a | Database for the \*arr stack |
| node_exporter | 9100 | scraped by Prometheus | Host metrics |
| promtail | 9080 | feeds Loki | Log shipping |
| SMB / NFS | 139, 445, 111, 2049 | | File shares |

### CT 103 — `docker-siem-stack` (192.168.10.31)

A SOCFortress / Wazuh-based SIEM lab.

| Service | Port | URL | Notes |
|---|---|---|---|
| **SOCFortress CoPilot** | 80, 443 | [192.168.10.31](http://192.168.10.31) | SIEM frontend |
| **Wazuh dashboard** | 5601 | [192.168.10.31:5601](https://192.168.10.31:5601) | OpenSearch / Kibana-derived UI |
| **Wazuh indexer** | 9200 | port only | OpenSearch API |
| **Wazuh agents** | 1514, 1515, 55000 | port only | Agent ingestion + API |
| **Graylog** | 9000 | [192.168.10.31:9000](http://192.168.10.31:9000) | Log management web UI |
| **Grafana** | 3000 | [192.168.10.31:3000](http://192.168.10.31:3000) | Metrics dashboards |
| **Portainer** | 9443 | [192.168.10.31:9443](https://192.168.10.31:9443) | Docker UI |
| **prometheus-blackbox** | 9116 | scraped by Prometheus | Synthetic probes |
| node_exporter | 9100 | | Host metrics |

### CT 201 — `zeus` (192.168.10.201)

OSINT / recon container. All outbound traffic goes through `gluetun` for IP isolation.

| Service | Port | URL | Notes |
|---|---|---|---|
| **SearXNG** | 8082 | [192.168.10.201:8082](http://192.168.10.201:8082) | Privacy-respecting metasearch |
| **Spiderfoot** | 5001 | [192.168.10.201:5001](http://192.168.10.201:5001) | OSINT automation framework |
| **Nessus** | 8834 | [192.168.10.201:8834](https://192.168.10.201:8834) | Vulnerability scanner |
| **recon-tools** | 8888 | [192.168.10.201:8888](http://192.168.10.201:8888) | Recon/OSINT toolkit web UI |
| **Shadowsocks** | 8388 | port only | gluetun SOCKS proxy entry |

### Other containers

| CT | Name | IP | Notes |
|---|---|---|---|
| 100 | `docker-zeus` | 192.168.10.209 | General Docker host (mostly Watchtower) |
| 106 | `cloudflared` | 192.168.10.229 | Cloudflare tunnel daemon |
| 107 | `rdtclient` | 192.168.10.205 | Real-Debrid downloader |
| 111 | `vault` | 192.168.10.27 | File vault — [Cockpit](https://192.168.10.27:9090) on 9090, SMB on 139/445 |
| 112 | `omada` | 192.168.10.200 | TP-Link Omada SDN controller — [https://192.168.10.200:8043](https://192.168.10.200:8043) |
| 117 | `cosmos-dashboard` | 192.168.10.60 | [Homelab dashboard](http://192.168.10.60) on port 80 |

### VMs

| VMID | Name | IP | Notes |
|---|---|---|---|
| 102 | `debian-gitea-zeus` | 192.168.10.25 | [Gitea](http://192.168.10.25:3000) on 3000 — self-hosted git |
| 110 | `debian` | n/a | Generic Debian dev VM |
| 115 | `servarr-vm` | n/a | Servarr migration target VM |

### Quick zeus health probe

```bash
ssh root@zeus 'pct list; qm list'
ssh root@zeus 'for ct in 100 103 105 106 107 111 112 117 201; do
  ip=$(pct exec $ct -- hostname -I 2>/dev/null | awk "{print \$1}")
  echo "CT $ct -> $ip"
done'
```

### Updating the zeus list

From titan (which has LAN access):

```bash
ssh titan 'for ip in 192.168.10.150 192.168.10.29 192.168.10.31 192.168.10.201 192.168.10.27 192.168.10.200 192.168.10.60 192.168.10.209 192.168.10.229 192.168.10.205 192.168.10.25; do
  echo "=== $ip ==="
  nmap -p- --min-rate 2000 -T4 --open -Pn $ip 2>/dev/null | grep "^[0-9]*/tcp"
done'
```

zeus listing captured **2026-04-30** via Atlas-routed access (titan acts as the LAN-side scanner; tailscale gates direct shell access via `root@zeus`).

## Travel workflow

```bash
ssh titan
tmux a              # attach to running session, or `tmux new -s plex`
# work
# Ctrl-b d to detach (keeps everything running)
```

See [`tmux/README.md`](tmux/) for the full keystroke reference.

## Claude Code integration

[`claude/`](claude/) versions the parts of `~/.claude/` worth syncing across machines. After cloning + symlinking (see bootstrap above), every Claude Code session on the host automatically gets:

### Status line

```
[caddy] ~/projects/caddy/src/foo  Sonnet 4.6 ctx:34%
```

`[project]` is the folder directly under `Projects/` or `projects/`, then the path with `$HOME` collapsed, the active model, and context-used percentage. Pure POSIX `sh`, runs identically on Mac and Linux. Source: [`claude/statusline-command.sh`](claude/statusline-command.sh).

### Slash commands

Six commands wired to homelab workflows in [`claude/commands/`](claude/commands/):

| Command | What |
|---|---|
| `/homelab-status` | Tight 5-line health check across titan (sessions/docker/disk/Caddy/Plex) |
| `/deploy-cinema` | Rebuild + redeploy the British Cinema static site |
| `/cf-add <subdomain> [--bypass]` | Add a new `*.harker.systems` service end-to-end (CF API + Caddy + reload) |
| `/cf-list` | Show every hostname currently routed by the harker.systems tunnel |
| `/travel-on` | Activate travel mode on titan + print manual checklist |
| `/travel-off` | Restore paused workloads on titan and verify |

Add new commands by dropping `name.md` into `claude/commands/` (with `description` and `allowed-tools` frontmatter) — the symlinks already in place mean they're picked up immediately.

### Top-level CLAUDE.md (project map)

[`claude/projects-claude-md-titan.md`](claude/projects-claude-md-titan.md) installs as `/home/stu/projects/CLAUDE.md` on titan. Claude Code walks up the directory tree finding `CLAUDE.md` files, so any session in any subfolder gets the project map (folder list + sizes + per-folder context links) loaded alongside the per-folder context. Mac equivalent at [`claude/projects-claude-md-mac.md`](claude/projects-claude-md-mac.md) → `~/Projects/CLAUDE.md`.

Per-folder `CLAUDE.md` files — one in each project folder under this repo and on titan — give Claude Code instant context about purpose, key files, common commands, and gotchas without re-deriving them from code. Live at e.g. [`caddy/CLAUDE.md`](caddy/CLAUDE.md), [`cloudflare/CLAUDE.md`](cloudflare/CLAUDE.md), [`travel-mode/CLAUDE.md`](travel-mode/CLAUDE.md), etc.

## Staying online while abroad

The full plan — pre-flight checklist, Caddy + Cloudflare Access gateway, resilience layer, break-glass paths — lives in Notion: [Travel Mode — Deep Remote-Access Plan](https://www.notion.so/352bb54b0db681d18b54f9d0d835ed9e).

Pocket runbook (the bare minimum from a hotel):

```bash
# 1. Confirm tailnet reach
tailscale status | grep -E 'titan|zeus|forge'

# 2. Attach to long-running tmux on titan
ssh titan 'tmux a -t plex'   # or `tmux new -s plex` first time

# 3. If SSH fails, jump via zeus over LAN
ssh -J zeus stu@192.168.10.80

# 4. Browser-only? Hit any *.harker.systems URL → CF Access OTP via email
#    (after Phase 1 of the Notion plan is deployed)
```

Break-glass when the normal path is blocked:

| Symptom | Fix |
|---|---|
| Tailscale UDP blocked at hotel | `tailscale up --tun=userspace-networking` to force DERP relay |
| Tailscale fully blocked | `cloudflared access ssh --hostname ssh.harker.systems` (Phase 5.B) |
| Titan unreachable, zeus alive | SSH zeus, `ssh stu@192.168.10.80`, then `sudo systemctl restart` whatever broke |
| Plex won't stream | check [Plex Pass relay status](https://app.plex.tv/desktop/#!/settings/server/<machine-id>/manage/remote-access) — falls back automatically |
| iPhone lost | use Latitude bootstrap kit (Phase 0.3) — Tailscale auth-key pre-stored, recovery codes via Vaultwarden |

Status of plan deployment is tracked in the Notion page's Section 6 status table.
