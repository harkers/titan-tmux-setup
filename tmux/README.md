# tmux (titan + Mac)

Persistent terminal sessions that survive SSH disconnects (titan use case) and survive logout/reboot (Mac use case via LaunchAgent + tmux-continuum).

## Install — titan (Debian)

```bash
sudo apt-get install tmux
cp .tmux.conf ~/.tmux.conf
```

## Install — any Linux host (zeus, nuc, cosmos, ...)

[`bootstrap-host.sh`](bootstrap-host.sh) is a single idempotent script that installs `tmux + mosh + fzf + git`, clones this repo to `~/tmux-setup`, symlinks `~/.tmux.conf`, installs tpm + all plugins, appends the SSH-agent shell snippet to `~/.bashrc` / `~/.zshrc`, and (if `~/projects/` exists) starts one detached session per folder.

Stream it over SSH on a fresh host:

```bash
ssh zeus 'bash -s' < ~/projects/tmux-setup/tmux/bootstrap-host.sh
ssh nuc 'bash -s' < ~/projects/tmux-setup/tmux/bootstrap-host.sh
ssh cosmos 'bash -s' < ~/projects/tmux-setup/tmux/bootstrap-host.sh
```

Or, once the repo is cloned on the host:

```bash
ssh zeus 'bash ~/tmux-setup/tmux/bootstrap-host.sh'
```

Re-running is safe — package install is a no-op, the conf symlink is refreshed, tpm reinstalls cleanly, and existing tmux sessions are skipped. The shell-rc snippet is marker-guarded so it's only appended once.

Env knobs:

| Var | Purpose |
|---|---|
| `SKIP_SESSIONS=1` | Install + configure only; don't spawn project sessions |
| `REPO_DIR=~/foo` | Override clone target (default `~/tmux-setup`) |
| `REPO_URL=...` | Use a fork/mirror instead of `harkers/tmux-setup` |

The script auto-detects apt / dnf / pacman / apk, and runs without `sudo` when invoked as root (e.g. on Proxmox LXC containers like `root@zeus`).

## Install — Mac (auto-restart on login)

```bash
brew install tmux mosh fzf
ln -sfn ~/projects/tmux-setup/tmux/.tmux.conf ~/.tmux.conf
git clone --depth 1 https://github.com/tmux-plugins/tpm ~/.tmux/plugins/tpm
~/.tmux/plugins/tpm/bin/install_plugins   # resurrect, continuum, yank, prefix-highlight, battery
```

Append the SSH-agent socket snippet to `~/.zshrc` so agent forwarding survives detach/reattach:

```bash
cat >> ~/.zshrc <<'EOF'

# tmux-setup: stable SSH agent socket — survives tmux detach/reattach
if [ -n "${SSH_AUTH_SOCK:-}" ] && [ -S "$SSH_AUTH_SOCK" ] && [ "$SSH_AUTH_SOCK" != "$HOME/.ssh/agent.sock" ]; then
    ln -sf "$SSH_AUTH_SOCK" "$HOME/.ssh/agent.sock"
fi
[ -S "$HOME/.ssh/agent.sock" ] && export SSH_AUTH_SOCK="$HOME/.ssh/agent.sock"
EOF
```

Register the LaunchAgent so all `~/projects/*` sessions come back on every login. The plist is versioned at [`dev.harkers.tmux-sessions.plist`](dev.harkers.tmux-sessions.plist) — it invokes [`start-mac.sh`](start-mac.sh), which sets `PROJECTS_DIR=~/projects` and Homebrew's `PATH` before calling [`start-all-sessions.sh`](start-all-sessions.sh).

```bash
cp ~/projects/tmux-setup/tmux/dev.harkers.tmux-sessions.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/dev.harkers.tmux-sessions.plist
```

Run any time on demand (idempotent — existing sessions are left alone):

```bash
bash ~/projects/tmux-setup/tmux/start-mac.sh
```

Logs at `~/Library/Logs/tmux-sessions.log`. tmux-continuum saves pane layouts every 15 min, tmux-resurrect restores them when the server starts again, so even after `tmux kill-server` or a reboot the working state is preserved.

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

Run [`start-all-sessions.sh`](start-all-sessions.sh) to spin up one detached session per project folder. Idempotent — re-run any time without disturbing existing sessions.

```bash
# titan (default PROJECTS_DIR=/home/stu/projects)
ssh titan 'bash /home/stu/projects/tmux/start-all-sessions.sh'

# Mac (wrapper sets PROJECTS_DIR=~/projects and Homebrew PATH)
bash ~/projects/tmux-setup/tmux/start-mac.sh

# Then attach
tmux a -t plex            # titan: radarr, kometa, caddy, cloudflare, etc.
                          # Mac:   plex-tools, media-server-mac, video-studio, etc.
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

## Plugins (via tpm)

| Plugin | What it gives you |
|---|---|
| **tmux-resurrect** | `prefix + Ctrl-s` saves session state to disk; `prefix + Ctrl-r` restores. Pane contents included. |
| **tmux-continuum** | Auto-saves every 15 min, auto-restores on next tmux server start. Survives reboot. |
| **tmux-yank** | Selections (mouse drag or copy-mode) auto-copy to the **system clipboard** — `pbcopy` on Mac, `xclip`/`xsel` on Linux. |
| **tmux-prefix-highlight** | Visible `PREFIX` indicator in the status bar while the prefix key is held — no more wondering whether the keystroke landed. |
| **tmux-battery** | Battery icon + percentage in the status bar. No-op on hosts without a battery. |

## Extras beyond defaults

- **Prefix + T** — fzf-driven popup session picker (centred floating window, lists every other session). Faster than `prefix + s`. Requires `fzf` installed.
- **Stable SSH agent socket** — panes use `$HOME/.ssh/agent.sock`, kept fresh by the shell-rc snippet appended by the bootstrap script (or copy-paste from the Mac install section above). Agent-forwarded `git push`, `ssh`, etc. keep working across tmux detach/reattach.
