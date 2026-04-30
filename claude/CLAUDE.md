# Claude Code config (versioned bits)

This folder versions the parts of `~/.claude/` that are useful across machines. Currently just the status line script. The full `~/.claude/settings.json` is **not** versioned because it has machine-specific state (hooks tied to local paths, MCP URLs, plugin lists).

## Status line script

`statusline-command.sh` is POSIX sh and runs identically on Mac and Linux. Reads session JSON from stdin, prints `[project] ~/path  Model ctx:NN%` with project name extracted as the folder directly under `Projects/` or `projects/` (case-insensitive).

## When editing this script

1. Test locally first — pipe fake session JSON, check the output:
   ```bash
   echo '{"workspace":{"current_dir":"'"$PWD"'"},"model":{"display_name":"test"}}' | sh statusline-command.sh
   echo
   ```
2. Sync to both machines:
   - Mac: `cp statusline-command.sh ~/.claude/`
   - titan: `rsync -av statusline-command.sh titan:~/.claude/statusline-command.sh`
3. Reload Claude Code (open a new session — it's read on each render)

## Don't

- Add color/emoji unless explicitly asked. The script intentionally uses only ANSI dim (`\033[2m`) so it's terminal-portable and doesn't fight with tmux/iTerm color schemes.
- Bake in absolute paths. `$HOME` is resolved at runtime so the same script works on Mac (`/Users/stu`) and titan (`/home/stu`).
- Move it to a different filename without updating both `~/.claude/settings.json` files (Mac + titan). The path is referenced by absolute string there.

## Cross-references

- `../tmux/CLAUDE.md` — tmux config that runs alongside this
- `../caddy/CLAUDE.md` etc. — per-project CLAUDE.mds that get auto-loaded when you cd into one of those folders
