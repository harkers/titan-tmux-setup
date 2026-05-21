# tmux config + session fleet (titan + Mac)

Persistent terminal sessions for all project folders.
- On titan: lives at `/home/stu/projects/tmux/` (rsync'd from this repo).
- On Mac: lives at `/Users/stu/projects/tmux-setup/tmux/` (this repo, in place).

## What's deployed

- `~/.tmux.conf` — symlink (Mac) or copy (titan) of this repo's `.tmux.conf` (Ctrl-b OR Ctrl-a prefix, mouse on, vim-style pane navigation, 256-colour, 50K history, tpm + resurrect + continuum)
- `start-all-sessions.sh` — creates one detached session per project folder, idempotent
- `start-mac.sh` — Mac wrapper that sets `PROJECTS_DIR=~/projects` + Homebrew `PATH`, then calls `start-all-sessions.sh`
- `dev.harkers.tmux-sessions.plist` — Mac LaunchAgent that runs `start-mac.sh` at login; installed at `~/Library/LaunchAgents/`

## Session conventions

- **One session per project folder** — name matches folder name (caddy, cloudflare, plex, kometa, etc.)
- Each session opens cd'd into its project directory
- Intro command picked by project type: `git status -sb` for git repos, `docker compose ps` for docker projects, `ls -la` otherwise
- The `pd-bulk` session is pre-existing (created 2026-04-27), not managed by this script

## Common tasks

```bash
# refresh sessions on titan
bash /home/stu/projects/tmux/start-all-sessions.sh

# refresh sessions on Mac
bash ~/projects/tmux-setup/tmux/start-mac.sh

# attach
tmux a -t plex
tmux a -t cloudflare

# pick interactively (inside any tmux session)
# prefix + s

# list all
tmux ls

# kill one
tmux kill-session -t <name>

# kill all (rare, blunt)
tmux kill-server
```

## Skip-list (in start-all-sessions.sh)

- `shield-apks` — data dump, not a project

Add to the `SKIP=` env in the script if more data-only folders appear.

## Gotcha

`((var++))` in bash returns the previous value as exit code. With `set -e`, this kills the script on the first iteration when `var` starts at 0. Use `var=$((var + 1))` instead.

## Cross-references

- [Travel workflow in tmux-setup README](../README.md#travel-workflow)
