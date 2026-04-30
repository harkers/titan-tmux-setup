# TigerVNC + XFCE on titan

Remote desktop for graphical access to titan over Tailscale. Mac's built-in Screen Sharing connects directly — no extra client needed.

## Install

```bash
sudo apt-get update
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    xfce4 xfce4-goodies tigervnc-standalone-server tigervnc-common dbus-x11 dbus-user-session \
    tightvncpasswd
```

## Configure (one-time, as the user that will run VNC)

```bash
mkdir -p ~/.vnc ~/.config/systemd/user

# Set password (replace 'YOUR_PASS_HERE')
echo -e 'YOUR_PASS_HERE\nYOUR_PASS_HERE\nn' | tightvncpasswd -f > ~/.vnc/passwd
chmod 600 ~/.vnc/passwd

# Drop the configs from this repo
cp xstartup ~/.vnc/xstartup
cp config ~/.vnc/config
chmod +x ~/.vnc/xstartup
cp vncserver.service ~/.config/systemd/user/

# Allow user services to keep running without an SSH login
sudo loginctl enable-linger $USER

systemctl --user daemon-reload
systemctl --user enable --now vncserver.service
```

## Verify

```bash
systemctl --user status vncserver.service
ss -tnlp | grep 5901    # should show Xtigervnc listening
```

## Connect from Mac

| Method | URL |
|---|---|
| Finder → ⌘K | `vnc://titan.tail1a2109.ts.net:5901` |
| Spotlight → "Screen Sharing" | hostname `titan.tail1a2109.ts.net:5901` |
| LAN | `vnc://192.168.10.80:5901` |

Then enter the VNC password.

## Files in this directory

| File | Maps to |
|---|---|
| [`xstartup`](xstartup) | `~/.vnc/xstartup` — script that runs when VNC session starts; launches XFCE |
| [`config`](config) | `~/.vnc/config` — VNC server defaults (geometry, security types) |
| [`vncserver.service`](vncserver.service) | `~/.config/systemd/user/vncserver.service` — systemd user service |

## Operating

```bash
# Restart (e.g. after changing geometry)
systemctl --user restart vncserver

# Stop
systemctl --user stop vncserver

# Logs
journalctl --user -u vncserver -f
```

## Change resolution

Edit `~/.vnc/config`:

```
geometry=2560x1440
```

Then `systemctl --user restart vncserver`.

## Change password

```bash
echo -e 'NEW_PASS\nNEW_PASS\nn' | tightvncpasswd -f > ~/.vnc/passwd
chmod 600 ~/.vnc/passwd
systemctl --user restart vncserver
```

## Security

- `localhost=no` in `config` exposes VNC on all interfaces. With Tailscale that's fine since Tailscale handles auth + encryption between machines. For LAN-only access change to `localhost=yes` and tunnel via SSH.
- `SecurityTypes=VncAuth,TLSVnc` enables both legacy + TLS-encrypted auth. Mac's Screen Sharing uses VncAuth by default.
- Don't expose port 5901 to the public internet.

## Window tiling in XFCE

Built-in:
- **Drag a window's title bar to a screen edge** → tiles that half/quarter
- **`Super` + `←` / `→` / `↑` / `↓`** → tile in that direction (configure in *Settings → Window Manager → Keyboard*)
- **Right-click title bar → Tile** submenu

When connected from Mac, ⌘ key sends as `Super`. If it doesn't, check Screen Sharing's keyboard preferences.
