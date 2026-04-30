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

## Connection cheatsheet

| Service | URL |
|---|---|
| Plex | `http://titan.tail1a2109.ts.net:32400` |
| Plex (LAN) | `http://192.168.10.80:32400` |
| Posterizarr UI | `http://titan.tail1a2109.ts.net:8000` |
| TigerVNC desktop | `vnc://titan.tail1a2109.ts.net:5901` |
| SSH | `ssh titan` (via tailscale, hostname resolves automatically) |

## Travel workflow

```bash
ssh titan
tmux a              # attach to running session, or `tmux new -s plex`
# work
# Ctrl-b d to detach (keeps everything running)
```

See [`tmux/README.md`](tmux/) for the full keystroke reference.
