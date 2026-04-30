# Cloudflare management for harker.systems

Idempotent Python scripts (stdlib only) that manage the `harker.systems` zone, tunnel ingress, and Access apps. Lives at `/home/stu/projects/cloudflare/`. Mirror in [titan-tmux-setup/cloudflare/](https://github.com/harkers/titan-tmux-setup/tree/main/cloudflare).

## Critical IDs (in `cf_common.py`)

| Constant | Value | Purpose |
|---|---|---|
| `HARKER_ZONE_ID` | `7753bd60f0d59784363e0c47d6ab32dc` | the harker.systems Cloudflare zone |
| `HARKER_TUNNEL_ID` | `8ba2b285-f8c1-464b-914e-f758c48d9e04` | the active tunnel |
| `HOMELAB_APP_ID` | `4ef2b00f-2dc2-4599-98e1-0bff66796155` | CF Access app for `*.harker.systems` |
| `DASHBOARD_APP_ID` | `cb58931c-b466-4fd5-a3ae-6884f6df84d3` | older Access app for `*.teamharker.com` |
| `DASHBOARD_AUD` | `4ed5eb6e...0ef102` | audTag of Dashboard app |
| `HOMELAB_AUD` | `433e68ae...c3c88e` | audTag of Homelab app |
| `CADDY_ORIGIN` | `http://192.168.10.80:80` | every new ingress points here |

## Token

`.env` lives next to the scripts on titan (`chmod 600`). On Mac, the loader auto-detects `/Users/stu/Projects/ordered-edge/.env.secrets`. Required scopes:
- Zone:DNS:Edit on harker.systems
- Account:Cloudflare Tunnel:Edit
- Account:Access: Apps and Policies:Edit (only for creating new apps)

## Daily-driver scripts

```bash
python3 add_service.py grafana            # gated
python3 add_service.py overseerr --bypass # public
python3 list_services.py                  # show all 56 routed hostnames
python3 remove_service.py grafana         # cleanup
```

## Bootstrap (one-shot, already run 2026-04-30)

`bootstrap/01_*` through `bootstrap/04_*` did the original 35-service rollout, Access app creation, audTag expansion, and SSH break-glass. All idempotent — re-running is safe but unnecessary.

## Gotchas

- **`add_service.py` only does the CF side.** You also need to add a site block to [`../caddy/Caddyfile`](../caddy/Caddyfile) and reload Caddy.
- **PATCH on Access apps fails** with our token (10405 method-not-allowed-for-scope). POST a new app instead, then update audTag references in tunnel rules.
- **Multiple tunnels on harker.systems** — see [memory: harker.systems CF tunnel topology](../../memory). Don't touch `*.harker.systems` wildcard A record (`80.5.36.105`) without a plan for Plex which depends on it.

## Cross-references

- [`../caddy/CLAUDE.md`](../caddy/CLAUDE.md) — what consumes the routes this creates
- [Travel-Resilience Sprint Log 2026-04-30](https://www.notion.so/352bb54b0db681038fd2d217846fd510)
- [Forge Cloudflare Zero Trust Setup](https://www.notion.so/338bb54b0db6814f8e30c209f90f3266) — the Clavis pattern this mirrors
