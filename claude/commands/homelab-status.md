---
description: One-shot health check of the titan homelab — sessions, docker, disk, Caddy, Plex
allowed-tools: Bash
---

Run a concise health check of titan and report it as a tight 5-line summary. Don't dump walls of output.

Check these in parallel where you can:
1. tmux session count: `ssh titan 'tmux ls 2>/dev/null | wc -l'`
2. Docker total + any unhealthy: `ssh titan 'docker ps --filter "health=unhealthy" --format "{{.Names}}"; echo TOTAL=$(docker ps -q | wc -l)'`
3. Disk: `ssh titan 'df -h / /var/www | tail -2'`
4. Critical containers state: `ssh titan 'docker inspect --format "{{.Name}} {{.State.Status}}" plex caddy cloudflared 2>/dev/null'`
5. Tunnel routing count: `cd /Users/stu/Projects/tmux-setup/cloudflare && python3 list_services.py 2>&1 | head -1`

Report findings concisely. Flag anything that looks anomalous (containers not running, disk >85%, etc.). If everything is healthy, one line is enough.
