# Caddy — *.harker.systems gateway on titan

Single reverse proxy that gives every titan + zeus service a clean URL on `*.harker.systems`, fronted by Cloudflare Access for auth.

```
Internet
  │
  ▼
Cloudflare Access (email/SSO check)
  │
  ▼
Cloudflare Tunnel — sso-home-lab (cloudflared on titan)
  │
  ▼ (origin: http://titan:80)
Caddy on titan (this directory)
  │
  ├─→ titan-local services (127.0.0.1:*)
  └─→ zeus services (192.168.10.x:*)
```

This file documents the deploy. The full plan, threat model, sequencing, and break-glass paths live in Notion: [Travel Mode — Deep Remote-Access Plan](https://www.notion.so/352bb54b0db681d18b54f9d0d835ed9e).

## Files

| Path | Purpose |
|---|---|
| `Caddyfile` | Host-to-backend routing for ~40 services |
| `docker-compose.yml` | Caddy container, host-mode, restart=unless-stopped |
| `README.md` | This file |

## Prerequisites (do these BEFORE the first `docker compose up`)

1. **Wildcard DNS in Cloudflare** — `*.harker.systems` CNAME → `18a78b3b-7b30-465f-b09f-4e6912daee1f.cfargotunnel.com` (proxied/orange cloud).
2. **Tunnel ingress** — in Cloudflare Zero Trust → Networks → Tunnels → `sso-home-lab` → Public Hostnames, add a catch-all route below the existing `plex.harker.systems` rule:
   - Subdomain: `*` · Domain: `harker.systems` · Service: `http://titan:80`
   - The existing `plex` rule remains and wins because it's more specific.
3. **Cloudflare Access application** — Zero Trust → Access → Applications → Add → Self-hosted:
   - Application Domain: `*.harker.systems`
   - Identity provider: One-time PIN (matches the Clavis / OE pattern)
   - Session duration: 24h
   - Default policy "Allow": `Emails: stuharker@gmail.com` + `Email domain: orderededge.co.uk`
4. **Bypass Access apps** for the public services (separate apps, more-specific domains, action=Bypass with Service Auth):
   - `overseerr.harker.systems` — guests submit media requests
   - `jellyseerr.harker.systems` — guests submit media requests
   - `nitter.harker.systems` — public Twitter mirror
   - `audiobookshelf.harker.systems` — has its own auth

## Deploy

```bash
# On macbook
rsync -av /Users/stu/Projects/titan-tmux-setup/caddy/ titan:/home/stu/projects/caddy/

# On titan
cd /home/stu/projects/caddy
docker compose up -d
docker logs -f caddy        # watch for "serving initial configuration"
```

## Verify

From a non-tailnet IP (phone hotspot is easiest):

```bash
# CF Access OTP gate active — expect 302 to a cloudflareaccess.com URL
curl -sI https://radarr.harker.systems/

# Bypass active — expect 200 directly from Overseerr
curl -sI https://overseerr.harker.systems/

# Existing Plex rule untouched
curl -sI https://plex.harker.systems/web
```

## Adding a service

1. Edit `Caddyfile` — pick a subdomain, decide whether it needs `cf_access_required` or is a guest-public bypass
2. Push to GitHub
3. `rsync` to titan and `docker exec caddy caddy reload --config /etc/caddy/Caddyfile`
4. If it's behind CF Access, no additional CF config needed (the wildcard application covers it). If it's a bypass, add a separate Access app with the specific subdomain and `Bypass` action.

## Caddy is HTTP-only

`auto_https off` is set in the global block. TLS termination happens at Cloudflare's edge. This means:

- Caddy listens on port 80 only.
- The container does not need to write to a certificate store.
- Caddy trusts the `Cf-Connecting-IP` and `Cf-Access-Authenticated-User-Email` headers because `trusted_proxies cloudflare` validates them against Cloudflare's published IP ranges.

If you ever want to expose Caddy *without* Cloudflare in front (e.g. tailnet-internal access), add a separate site block with `tls internal` or use Tailscale's cert provisioning.

## Reload, troubleshoot, and tail logs

```bash
# Reload config without restarting the container
docker exec caddy caddy reload --config /etc/caddy/Caddyfile

# Validate the Caddyfile before reloading
docker exec caddy caddy validate --config /etc/caddy/Caddyfile

# Tail Caddy logs
docker logs -f caddy

# Check what Caddy is routing for a specific host
curl -s --resolve radarr.harker.systems:80:127.0.0.1 http://radarr.harker.systems/
```

## Why not Authentik forward-auth?

Two reasons:
1. CF Access enforces auth at the edge — before any traffic enters your network. Authentik forward-auth still requires the request to reach titan first.
2. The OE Clavis stack already uses CF Access for `*.orderededge.co.uk`. Reusing the same IdP keeps one identity surface.

Authentik on titan stays for the OE app stack (where it federates with M365 / Google) and for any tailnet-only services that want their own SSO.

## What stays out of Caddy

- **Plex** — keeps its existing dedicated tunnel route. Plex needs the public IP for direct-play and breaks behind a generic reverse proxy.
- **Authentik / Vaultwarden / Ollama API / DBs** — tailnet-only; access via Tailscale IP.
- **Proxmox noVNC console** — works through Caddy with websockets, but if console is laggy, fall back to direct Tailscale.
