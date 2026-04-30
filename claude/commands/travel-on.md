---
description: Activate travel mode on titan — pauses bandwidth-hungry workloads (Kometa, OpenClaw MCPs, Ollama)
allowed-tools: Bash
---

Run travel-mode `on` on titan and report what got paused. After this completes:

```bash
ssh titan travel-mode on
```

Then immediately follow up with the manual reminders the script prints — particularly:
1. **Plex web → Settings → Network → Remote Streaming Quality** — cap at 4 Mbps so transcodes fit hotel bandwidth.
2. **Mac Tailscale** — switch exit node to Forge if it's been activated (Phase 0.1 of the Travel Mode plan).

Do not run any heavy operations after this command — the point is to leave titan idle.
