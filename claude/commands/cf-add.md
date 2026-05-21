---
description: Add a new *.harker.systems service via CF API + tunnel ingress
argument-hint: <subdomain> [--bypass]
allowed-tools: Bash, Read, Edit
---

Add a new service to `*.harker.systems`. Two steps — Cloudflare side first, then Caddy.

**Step 1 — Cloudflare:** run the API helper from this repo (it adds the CNAME and the tunnel ingress rule):

```bash
cd /Users/stu/Projects/tmux-setup/cloudflare && python3 add_service.py $ARGUMENTS
```

**Step 2 — Caddy:** ask the user what backend `<subdomain>.harker.systems` should reverse-proxy to (e.g. `127.0.0.1:8000` for a titan-local service or `192.168.10.29:7878` for a zeus service). Then append the standard site block to `/Users/stu/Projects/tmux-setup/caddy/Caddyfile`:

```caddyfile
http://<subdomain>.harker.systems {
	reverse_proxy <backend> {
		lb_try_duration 4s
		lb_try_interval 250ms
		transport http {
			dial_timeout 8s
		}
	}
}
```

Insert it in the right section (titan-local / zeus servarr / SIEM / OSINT / infra). Then rsync to titan and reload Caddy:

```bash
rsync -av /Users/stu/Projects/tmux-setup/caddy/Caddyfile titan:/home/stu/projects/caddy/Caddyfile
ssh titan 'docker exec caddy caddy reload --config /etc/caddy/Caddyfile'
```

Confirm the route works by curling through CF:

```bash
curl -sI -A 'Mozilla/5.0' -H 'Accept: text/html' "https://<subdomain>.harker.systems/" | head -3
```

For a gated service (no `--bypass` arg) you should see `HTTP/2 302` to `forgeshield.cloudflareaccess.com`. For a bypass service, expect `HTTP/2 200` (or whatever the backend returns).

Don't commit the Caddyfile change automatically — let the user review the diff and commit themselves.
