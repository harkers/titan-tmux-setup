# Slash commands for Claude Code

Versioned slash commands for the homelab + travel workflows we built. Each `.md` file becomes a `/<name>` command in Claude Code, available from any project directory once symlinked into `~/.claude/commands/`.

## Available commands

| Command | What it does |
|---|---|
| `/homelab-status` | Tight health check across titan (tmux/docker/disk/Caddy/Plex) + tunnel routing count |
| `/deploy-cinema` | Rebuild and deploy the British Cinema static site (calls deploy.sh on titan) |
| `/cf-add <subdomain> [--bypass]` | Add a new *.harker.systems service: CF API + Caddyfile + reload |
| `/cf-list` | List every hostname currently routed by the harker.systems tunnel |
| `/travel-on` | Pause bandwidth-hungry workloads on titan + show manual checklist |
| `/travel-off` | Restore paused workloads on titan and verify |

## Install

User-scope (works in any directory you launch Claude Code from):

```bash
# Mac
ln -sfn /Users/stu/Projects/tmux-setup/claude/commands/* ~/.claude/commands/

# titan
ssh titan 'ln -sfn /home/stu/projects/claude/commands/* ~/.claude/commands/'
```

Symlinks beat copies because edits to the repo flow through automatically — no need to re-deploy after a tweak.

## Adding a new command

1. Write `name.md` in this folder. Frontmatter:
   - `description:` — shows in `/help`
   - `argument-hint:` (optional) — tab-completion hint
   - `allowed-tools:` — which tools the command can call (Bash, Read, Edit, etc.)
2. Body of the .md is the prompt sent to Claude when invoked. Reference `$ARGUMENTS` for whatever followed the command name.
3. Commit + push. The symlink installs are already in place.

## Why version these instead of just keeping them in `~/.claude/commands/`?

- They reference repo-relative paths (`/Users/stu/Projects/tmux-setup/cloudflare/list_services.py` etc.). The repo IS the source of truth.
- A new machine setup gets all your commands by cloning the repo + running the symlink line.
- They evolve alongside the scripts they call. If `add_service.py` grows a new flag, the slash command's `argument-hint` should follow.
