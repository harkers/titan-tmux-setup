# tmux on titan

Persistent terminal sessions that survive SSH disconnects. Use this when you SSH from a travelling laptop and want work to continue when you close the lid.

## Install

```bash
sudo apt-get install tmux
cp .tmux.conf ~/.tmux.conf
```

## Daily commands

```bash
# First time (or after reboot)
ssh titan
tmux new -s plex       # creates session named "plex"

# Reconnecting (most of the time)
ssh titan
tmux a                 # attach to existing session

# List sessions
tmux ls

# Kill a session (rare)
tmux kill-session -t plex
```

## Connect via mosh on flaky links

For travel, replace `ssh` with `mosh` — it survives roaming between cellular and hotel WiFi, and reconnects without re-authenticating. Installed on Mac (`brew install mosh`) and titan (`apt install mosh`).

```bash
mosh titan                   # opens a shell on titan, survives sleep/roaming
mosh titan -- tmux a -t plex # attach to a tmux session via mosh
```

mosh uses UDP 60000-61000 to titan's tailnet IP. If Tailscale itself is blocked (some hotels, some countries), fall back to `cloudflared access ssh` (Phase 5.B in the [Travel Mode plan](https://www.notion.so/352bb54b0db681d18b54f9d0d835ed9e)) — different layer, complementary.

## One session per project

Run [`start-all-sessions.sh`](start-all-sessions.sh) on titan to spin up one detached session per `/home/stu/projects/*/` folder. Idempotent — re-run it any time without disturbing existing sessions.

```bash
ssh titan 'bash /home/stu/projects/tmux/start-all-sessions.sh'

# Then on next attach
ssh titan
tmux a -t plex            # or radarr, kometa, caddy, cloudflare, etc.
# inside tmux: Ctrl-b s   for interactive session picker
```

Each session opens already `cd`'d into its project. The script picks an appropriate intro command per project type:

- **git repos** — runs `git status -sb` so you see uncommitted work right away
- **docker projects** — runs `docker compose ps` to show container state
- **everything else** — runs `ls -la`

To switch between sessions without leaving tmux: prefix + `s` (interactive picker), or `tmux switch-client -t <name>` from inside.

## Keystrokes inside tmux

The **prefix** is `Ctrl-b` (or `Ctrl-a` with this config). Press it, release, then press the next key.

| Keystroke | Does |
|---|---|
| **`Ctrl-b d`** | **Detach** — leave session running, return to plain shell |
| `Ctrl-b c` | New window (like a new tab) |
| `Ctrl-b 1` / `2` / `3` | Switch to window 1/2/3 |
| `Ctrl-b ,` | Rename current window |
| `Ctrl-b \|` | Split pane vertically (this config) |
| `Ctrl-b -` | Split pane horizontally (this config) |
| `Ctrl-b h/j/k/l` | Move between panes (vim-style, this config) |
| `Ctrl-b z` | Zoom current pane to fullscreen (toggle) |
| `Ctrl-b [` | Scroll/copy mode (`q` to exit, arrow keys to scroll) |
| `Ctrl-b x` | Close current pane (asks confirmation) |
| `Ctrl-b r` | Reload `~/.tmux.conf` (this config) |

Mouse is enabled — click panes to switch, drag borders to resize, scroll naturally.

## Recommended layout

```bash
ssh titan
tmux new -s plex
cd /home/stu/projects/plex-overlay
claude                 # main work pane

# Ctrl-b c → new window: monitor logs
tail -F /home/stu/projects/posterizarr/cycle.log /home/stu/projects/posterizarr/repair_plex_xml.log

# Ctrl-b c → new window: ad-hoc shell

# Ctrl-b 1 → back to claude

# Ctrl-b d → detach when done
```

Next morning, anywhere:

```bash
ssh titan
tmux a    # exactly where you left off
```

## Why this config

- `mouse on` — modern, intuitive
- `prefix2 C-a` — alternative prefix that doesn't conflict with bash's `Ctrl-b`
- `history-limit 50000` — long scrollback in panes
- `renumber-windows on` — windows stay sequentially numbered when you close one
- Vim-style pane navigation (`hjkl`)
- `|` / `-` for splits (more intuitive than `%` / `"`)
