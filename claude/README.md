# Claude Code config

Versioned bits of `~/.claude/` that are useful across Mac + titan. Currently just the status line; add more here when there's something worth syncing across machines (slash commands, hook scripts, etc.).

## Files

| File | Purpose |
|---|---|
| `statusline-command.sh` | Renders the bottom-of-screen status line in every Claude Code session. POSIX sh, no Mac/Linux differences. Reads session JSON from stdin (Claude Code passes it), prints `[project] ~/path  Model ctx:NN%`. |
| `settings.example.json` | Drop-in snippet for `~/.claude/settings.json` to wire up the script. Don't replace the full settings.json — just add the `statusLine` block. |

## What you see

```
[caddy] ~/projects/caddy/src/foo  Sonnet 4.6 ctx:34%
```

- `[project]` — folder directly under `Projects/` or `projects/` (case-insensitive)
- the full path with `$HOME` collapsed to `~`
- the active model
- `ctx:NN%` after the first message in the session

When cwd is outside any `Projects/` tree, the `[project]` bracket is omitted.

## Install on a new machine

```bash
mkdir -p ~/.claude
cp claude/statusline-command.sh ~/.claude/statusline-command.sh
chmod +x ~/.claude/statusline-command.sh
```

Then edit `~/.claude/settings.json` to add the `statusLine` block (see `settings.example.json`). The path inside the command differs by OS:

- Mac: `sh /Users/stu/.claude/statusline-command.sh`
- titan: `sh /home/stu/.claude/statusline-command.sh`

To test without launching Claude Code, pipe a fake session JSON:

```bash
echo '{"workspace":{"current_dir":"/home/stu/projects/caddy"},"model":{"display_name":"Sonnet 4.6"}}' | sh ~/.claude/statusline-command.sh
echo
```

You should see `[caddy] ~/projects/caddy  Sonnet 4.6` (dimmed).

## What's *not* in this repo

`~/.claude/settings.json` itself — too much machine-specific state in there (hooks tied to local paths, MCP server URLs, plugin enable lists). Only the status line script + the snippet to wire it up are versioned.

## Cross-references

- [titan-tmux-setup top-level README](../README.md) — fits next to caddy/cloudflare/tmux/vnc/cron/posterizarr/travel-mode/british-cinema as another self-contained project folder
- Per-project `CLAUDE.md` files (in every `/home/stu/projects/*/`) — what gets loaded *into* the session when you cd there
