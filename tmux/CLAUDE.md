# tmux config + session fleet on titan

Persistent terminal sessions for all `/home/stu/projects/*` folders. Lives at `/home/stu/projects/tmux/`.

## What's deployed

- `~/.tmux.conf` on titan (Ctrl-b OR Ctrl-a prefix, mouse on, vim-style pane navigation, 256-colour, 50K history)
- `start-all-sessions.sh` — creates one detached session per project folder, idempotent

## Session conventions

- **One session per project folder** — name matches folder name (caddy, cloudflare, plex, kometa, etc.)
- Each session opens cd'd into its project directory
- Intro command picked by project type: `git status -sb` for git repos, `docker compose ps` for docker projects, `ls -la` otherwise
- The `pd-bulk` session is pre-existing (created 2026-04-27), not managed by this script

## Common tasks

```bash
# refresh sessions (adds any new /home/stu/projects/* folders)
bash /home/stu/projects/tmux/start-all-sessions.sh

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
