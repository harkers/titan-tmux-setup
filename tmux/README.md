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
