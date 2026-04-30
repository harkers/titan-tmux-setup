# Caddy on titan

Reverse proxy for `*.harker.systems`. Lives at `/home/stu/projects/caddy/`. Mirror in [titan-tmux-setup/caddy/](https://github.com/harkers/titan-tmux-setup/tree/main/caddy).

## Architecture

```
Cloudflare Tunnel "harker.systems" (8ba2b285-...) ──► http://192.168.10.80:80 ──► Caddy ──► fan-out by Host
                                                                                      ├─► 127.0.0.1:* (titan-local)
                                                                                      └─► 192.168.10.x:* (zeus services)
```

The tunnel itself runs on cosmos CT 115 (`cloudflared-opti-pve`). It can reach titan over LAN. CF Access enforces auth at the **tunnel ingress level** via audTag — Caddy receives only authenticated requests for protected services and never sees a JWT on bypass services.

## Files

- `Caddyfile` — 35 site blocks, all prefixed `http://` to force port-80-only
- `docker-compose.yml` — `caddy:2-alpine` in `network_mode: host`
- `README.md` — public-facing docs

## Common tasks

```bash
# reload after a Caddyfile edit
docker exec caddy caddy reload --config /etc/caddy/Caddyfile

# validate before reload
docker exec caddy caddy validate --config /etc/caddy/Caddyfile

# tail logs
docker logs -f caddy

# test routing without leaving titan
curl -sI -H 'Host: radarr.harker.systems' http://127.0.0.1/
```

## Gotchas (from incidents 2026-04-30)

- **`auto_https off` alone doesn't stop port 443 binding.** Caddy still tries to bind :443 for HTTPS redirects. Use `http://` prefix on every site block to force port 80 only.
- **`trusted_proxies cloudflare` needs the `caddy-cloudflare-ip` plugin** not present in `caddy:2-alpine`. Drop it — tunnel-only ingress means X-Forwarded-For doesn't matter.
- **Zeus servarr CT 105 has IO stalls** during swap pressure. Without retries, brief stalls become user-facing 502s. Every reverse_proxy now has `lb_try_duration 4s` + `transport.dial_timeout 8s` to ride them out.

## Adding a service

1. Add the CF side via [`../cloudflare/add_service.py`](../cloudflare/) (CNAME + tunnel ingress)
2. Add a site block here in `Caddyfile` (use the existing block-form template with retries)
3. `docker exec caddy caddy reload --config /etc/caddy/Caddyfile`

## Cross-references

- [`../cloudflare/CLAUDE.md`](../cloudflare/CLAUDE.md) — DNS + tunnel + Access management
- [`../travel-mode/CLAUDE.md`](../travel-mode/CLAUDE.md) — bandwidth saver that runs alongside this
- [Travel-Resilience Sprint Log 2026-04-30](https://www.notion.so/352bb54b0db681038fd2d217846fd510) — full deployment story
