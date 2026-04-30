---
description: Deactivate travel mode on titan — restore paused workloads + crontab
allowed-tools: Bash
---

Run travel-mode `off` on titan and report what was restored.

```bash
ssh titan travel-mode off
```

Then verify the resumed state:
- `ssh titan tmux ls | wc -l` (sessions still alive)
- `ssh titan docker ps --filter status=running --format "{{.Names}}" | wc -l` (containers running)

If anything that was paused didn't come back, tell me explicitly. Don't bury it.
