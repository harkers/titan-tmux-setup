# titan-tmux-setup

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
| [`posterizarr/`](posterizarr/) | docker-compose, auto-recovery cycle script, Plex DB poison-repair script |
| [`cron/`](cron/) | All `/etc/cron.d/` entries that keep the homelab healthy |

## Quick recovery / new-machine bootstrap

```bash
git clone https://github.com/harkers/titan-tmux-setup.git ~/titan-tmux-setup

# tmux
cp ~/titan-tmux-setup/tmux/.tmux.conf ~/

# VNC (after installing xfce4 + tigervnc-standalone-server + tightvncpasswd)
mkdir -p ~/.vnc ~/.config/systemd/user
cp ~/titan-tmux-setup/vnc/{xstartup,config} ~/.vnc/
cp ~/titan-tmux-setup/vnc/vncserver.service ~/.config/systemd/user/
echo -e 'PASSWORD\nPASSWORD\nn' | tightvncpasswd -f > ~/.vnc/passwd
chmod 600 ~/.vnc/passwd
sudo loginctl enable-linger $USER
systemctl --user enable --now vncserver.service

# Posterizarr (after Docker + image pulled)
mkdir -p /home/stu/projects/posterizarr/{config,assets,assetsbackup,manualassets,watcher}
cp ~/titan-tmux-setup/posterizarr/docker-compose.yml /home/stu/projects/posterizarr/
cp ~/titan-tmux-setup/posterizarr/{cycle.sh,repair_plex_xml.sh} /home/stu/projects/posterizarr/
chmod +x /home/stu/projects/posterizarr/{cycle.sh,repair_plex_xml.sh}
# Edit config.json with your TMDb v4 token, Fanart key, Plex token

# Cron
sudo cp ~/titan-tmux-setup/cron/* /etc/cron.d/   # adjust paths first
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

## Travel workflow

```bash
ssh titan
tmux a              # attach to running session, or `tmux new -s plex`
# work
# Ctrl-b d to detach (keeps everything running)
```

See [`tmux/README.md`](tmux/) for the full keystroke reference.
