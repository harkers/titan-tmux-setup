# Mac ~/Projects map

This file lives at `/Users/stu/Projects/CLAUDE.md` on the Mac. Claude Code walks up the directory tree finding `CLAUDE.md` files, so any session started in any subfolder gets this map plus the global `~/.claude/CLAUDE.md` (which has the Notion + brand + tooling preferences).

## Active projects

| Folder | Purpose | tmux session | Notion |
|---|---|---|---|
| `ordered-edge/` | OrderedEDGE audit practice — orderededge.co.uk site, Lens Auditor, M365 infra, ProPharma engagement | `ordered-edge` | [📦 OrderedEDGE — Products](https://www.notion.so/339bb54b0db6817ba41ef00d1e848e2d) |
| `fidelex/` | Fidelex master brand — parent workspace for privacy-ops product strategy | `fidelex` | [📘 Fidelex — Products](https://www.notion.so/33fbb54b0db681079cdcc7d3b6938bff) |
| `orderededge-agents/` | Lens Auditor + Python Agent SDK + FastMCP for cert-authenticated M365 audits | `orderededge-agents` | (linked from OE Platform) |
| `py-plex/` | Homelab provisioning + OSINT intelligence platform (Proxmox CTs, Docker stacks, NordVPN gluetun) | `py-plex` | [🏗️ Platform & Infrastructure](https://www.notion.so/339bb54b0db6815fb5dbe05b12c40409) |
| `tmux-setup/` | Homelab config repo (Caddy, Cloudflare scripts, tmux, VNC, travel-mode, Claude config). Origin of slash commands + status line. | — | (this repo) |

## Quick connect to titan

```bash
mosh titan                                    # survives sleep/roam (preferred)
ssh titan                                     # plain
ssh -J zeus stu@192.168.10.80                 # jump via zeus if Tailscale flaky
cloudflared access ssh --hostname ssh.harker.systems   # break-glass when Tailscale fully blocked
```

After connect:

```bash
tmux a -t <project>      # caddy / cloudflare / plex / kometa / etc.
# or interactive picker
# Ctrl-b s   (or Ctrl-a s)
```

## Slash commands (work from any project here)

`/homelab-status` `/cf-list` `/cf-add` `/deploy-cinema` `/travel-on` `/travel-off` — all defined in [`tmux-setup/claude/commands/`](tmux-setup/claude/commands/) and symlinked into `~/.claude/commands/`.

## Brand + tooling rules (from global `~/.claude/CLAUDE.md`)

- Always "OrderedEDGE" (one word), "Fidelex" (single capital F), "UK GDPR"
- UK English spelling everywhere
- Clickable markdown links — never bare URLs
- Pydantic-style schemas with enums when dispatching subagents

## Cross-references

- Global rules + Notion workspace map: [`~/.claude/CLAUDE.md`](~/.claude/CLAUDE.md)
- Homelab tooling repo: [tmux-setup](https://github.com/harkers/tmux-setup)
- titan project map: `/home/stu/projects/CLAUDE.md` (visible after `mosh titan`)
