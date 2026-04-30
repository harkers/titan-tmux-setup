# TigerVNC + XFCE on titan

Browser/native-VNC-friendly desktop on titan, port `5901`, accessible via Tailscale only. Lives at `/home/stu/projects/vnc/`.

## What's deployed

- `~/.vnc/xstartup` — XFCE launcher
- `~/.vnc/config` — TigerVNC params
- `~/.config/systemd/user/vncserver.service` — starts vncserver `:1` at login
- `loginctl enable-linger stu` — keeps user services running after disconnect

## Connect

```bash
# Mac (native)
open vnc://titan.tail1a2109.ts.net:5901

# Mac (port-forward + Finder)
ssh -L 5901:localhost:5901 titan
open vnc://localhost:5901

# iPhone
VNC Viewer iOS app → vnc://titan.tail1a2109.ts.net:5901
```

Password lives in `~/.vnc/passwd` (set with `tightvncpasswd`).

## Common tasks

```bash
# state
systemctl --user status vncserver

# restart
systemctl --user restart vncserver

# view geometry/settings
cat ~/.vnc/config

# kill a frozen session
vncserver -kill :1
```

## Gotcha

If `xstartup` exits immediately (typical when XFCE deps missing), the vncserver process disappears. Required packages: `xfce4 tigervnc-standalone-server tightvncpasswd`. The xstartup file in this folder is the known-good version.

## Travel-mode angle

VNC is **tailnet-only** by design — no Cloudflare Tunnel, no CF Access. If Tailscale is blocked, fall back to the `cloudflared access ssh` SSH break-glass and use a terminal-based workflow instead.

## Cross-references

- [Phase 4.3 GUI fallback in the Travel Mode plan](https://www.notion.so/352bb54b0db681d18b54f9d0d835ed9e)
- [`../tmux/CLAUDE.md`](../tmux/CLAUDE.md) — terminal-based alternative when VNC is unreachable
