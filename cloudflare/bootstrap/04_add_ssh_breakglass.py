#!/usr/bin/env python3
"""Phase 5.B: cloudflared SSH break-glass for titan.

When Tailscale is blocked at a hotel/country, cloudflared can tunnel
SSH over HTTPS via Cloudflare. Adds:
  1. CNAME ssh.harker.systems -> harker.systems tunnel
  2. Tunnel ingress rule: ssh.harker.systems -> ssh://192.168.10.80:22
  3. CF Access app for ssh.harker.systems with same policy

After this, from any machine: cloudflared access ssh --hostname ssh.harker.systems
"""
import json
import sys
import urllib.request
import urllib.error

ENV_PATH = "/Users/stu/Projects/ordered-edge/.env.secrets"
HARKER_ZONE_ID = "7753bd60f0d59784363e0c47d6ab32dc"
HARKER_TUNNEL_ID = "8ba2b285-f8c1-464b-914e-f758c48d9e04"
TUNNEL_CNAME = f"{HARKER_TUNNEL_ID}.cfargotunnel.com"

OLD_AUD = "4ed5eb6e5211b129897b7a53b853670f4802d17d8a118092262d078a350ef102"
NEW_AUD = "433e68aefb169f3a03d85260590aa8a4804f9f3cc435ed3bcfce2f999dc3c88e"


def load_env():
    token = account = None
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("CF_API_TOKEN="):
                token = line.split("=", 1)[1].strip("'\"")
            elif line.startswith("CF_ACCOUNT_ID="):
                account = line.split("=", 1)[1].strip("'\"")
    return token, account


def cf(method, url, token, body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read())


def add_cname(token):
    url = (
        f"https://api.cloudflare.com/client/v4/zones/{HARKER_ZONE_ID}/dns_records"
    )
    # check if already exists
    r = cf("GET", f"{url}?name=ssh.harker.systems", token)
    if r.get("result"):
        print(f"  ssh.harker.systems already exists, skipping CNAME")
        return
    body = {
        "type": "CNAME",
        "name": "ssh.harker.systems",
        "content": TUNNEL_CNAME,
        "ttl": 1,
        "proxied": True,
        "comment": "phase 5.B SSH break-glass 2026-04-30",
    }
    r = cf("POST", url, token, body)
    print(f"  CNAME ssh.harker.systems -> {'OK' if r.get('success') else r.get('errors')}")


def add_tunnel_ingress(token, account):
    cfg_url = (
        f"https://api.cloudflare.com/client/v4/accounts/{account}"
        f"/cfd_tunnel/{HARKER_TUNNEL_ID}/configurations"
    )
    cfg = cf("GET", cfg_url, token)
    config = cfg["result"]["config"]
    ingress = config["ingress"]

    if any(r.get("hostname") == "ssh.harker.systems" for r in ingress):
        print("  ssh.harker.systems already in ingress, skipping")
        return

    new_rule = {
        "hostname": "ssh.harker.systems",
        "service": "ssh://192.168.10.80:22",
        "originRequest": {
            "access": {
                "audTag": [OLD_AUD, NEW_AUD],
                "required": True,
                "teamName": "harkersystems",
            }
        },
    }
    catchall_idx = next(
        (i for i, r in enumerate(ingress) if "hostname" not in r), len(ingress)
    )
    ingress.insert(catchall_idx, new_rule)
    config["ingress"] = ingress

    r = cf("PUT", cfg_url, token, {"config": config})
    print(
        f"  tunnel ingress -> {'OK v' + str(r['result']['version']) if r.get('success') else r.get('errors')}"
    )


def main():
    token, account = load_env()
    print("Phase 5.B SSH break-glass setup:")
    add_cname(token)
    add_tunnel_ingress(token, account)
    print("\nNext: install cloudflared on your Mac if not already there:")
    print("  brew install cloudflared")
    print("\nUsage abroad when Tailscale is blocked:")
    print("  ssh -o ProxyCommand='cloudflared access ssh --hostname %h' titan-cf")
    print("\nOr add to ~/.ssh/config:")
    print("  Host titan-cf")
    print("    HostName ssh.harker.systems")
    print("    User stu")
    print("    ProxyCommand cloudflared access ssh --hostname %h")


if __name__ == "__main__":
    main()
