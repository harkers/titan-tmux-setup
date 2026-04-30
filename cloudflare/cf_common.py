"""Shared helpers for the harker.systems Cloudflare management scripts.

Each script should `from cf_common import load_env, cf, HARKER_*`.

Env loading order (first hit wins):
  1. CF_API_TOKEN + CF_ACCOUNT_ID env vars
  2. ./.env in the current working directory
  3. /home/stu/projects/cloudflare/.env (titan deploy path)
  4. /Users/stu/Projects/ordered-edge/.env.secrets (Mac dev path)

Token scopes required for the operations in this folder:
  - Zone:DNS:Edit on harker.systems
  - Account:Cloudflare Tunnel:Edit
  - Account:Access: Apps and Policies:Edit
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# ─── constants ────────────────────────────────────────────────────────────

HARKER_ZONE_ID = "7753bd60f0d59784363e0c47d6ab32dc"
HARKER_TUNNEL_ID = "8ba2b285-f8c1-464b-914e-f758c48d9e04"
TUNNEL_CNAME = f"{HARKER_TUNNEL_ID}.cfargotunnel.com"

# audTags currently accepted by harker.systems tunnel rules.
# Both included for backwards compatibility with sessions opened on
# *.teamharker.com (DASHBOARD_AUD) and *.harker.systems (HOMELAB_AUD).
DASHBOARD_AUD = "4ed5eb6e5211b129897b7a53b853670f4802d17d8a118092262d078a350ef102"
HOMELAB_AUD = "433e68aefb169f3a03d85260590aa8a4804f9f3cc435ed3bcfce2f999dc3c88e"
DEFAULT_AUDTAGS = [DASHBOARD_AUD, HOMELAB_AUD]

TEAM_NAME = "harkersystems"
HOMELAB_APP_ID = "4ef2b00f-2dc2-4599-98e1-0bff66796155"
DASHBOARD_APP_ID = "cb58931c-b466-4fd5-a3ae-6884f6df84d3"

# Where Caddy listens — every tunnel rule routes here, Caddy fans out by Host.
CADDY_ORIGIN = "http://192.168.10.80:80"

ENV_SEARCH = [
    "./.env",
    "/home/stu/projects/cloudflare/.env",
    "/Users/stu/Projects/ordered-edge/.env.secrets",
]


def load_env() -> tuple[str, str]:
    """Return (CF_API_TOKEN, CF_ACCOUNT_ID) or exit with a helpful error."""
    token = os.environ.get("CF_API_TOKEN")
    account = os.environ.get("CF_ACCOUNT_ID")
    if token and account:
        return token, account

    for path in ENV_SEARCH:
        p = Path(path)
        if not p.is_file():
            continue
        for line in p.read_text().splitlines():
            line = line.strip()
            if line.startswith("CF_API_TOKEN=") and not token:
                token = line.split("=", 1)[1].strip("'\"")
            elif line.startswith("CF_ACCOUNT_ID=") and not account:
                account = line.split("=", 1)[1].strip("'\"")
        if token and account:
            return token, account

    sys.exit(
        "missing CF_API_TOKEN or CF_ACCOUNT_ID — set as env vars, "
        "or create .env in this directory, see .env.example"
    )


def cf(method: str, url: str, token: str, body: dict | None = None) -> dict:
    """Make a Cloudflare API request and return the parsed JSON response."""
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors="replace")
        try:
            return json.loads(body_text)
        except json.JSONDecodeError:
            return {"error": body_text, "status": e.code}


# ─── small helpers ────────────────────────────────────────────────────────


def api(account: str, *path: str) -> str:
    return f"https://api.cloudflare.com/client/v4/accounts/{account}/" + "/".join(path)


def zone(zone_id: str, *path: str) -> str:
    return f"https://api.cloudflare.com/client/v4/zones/{zone_id}/" + "/".join(path)


def tunnel_config(account: str) -> str:
    return api(account, f"cfd_tunnel/{HARKER_TUNNEL_ID}/configurations")
