#!/usr/bin/env python3
"""Add 34 *.harker.systems CNAMEs + tunnel ingress rules.

Reads CF token + account from /Users/stu/Projects/ordered-edge/.env.secrets.
Targets the harker.systems tunnel (8ba2b285...) — NOT titan-home.
All routes terminate at titan:80 where Caddy will route by Host header.
"""
import json
import os
import sys
import time
import urllib.request
import urllib.error

ENV_PATH = "/Users/stu/Projects/ordered-edge/.env.secrets"
HARKER_ZONE_ID = "7753bd60f0d59784363e0c47d6ab32dc"
HARKER_TUNNEL_ID = "8ba2b285-f8c1-464b-914e-f758c48d9e04"
TUNNEL_CNAME = f"{HARKER_TUNNEL_ID}.cfargotunnel.com"
CADDY_ORIGIN = "http://192.168.10.80:80"
AUDTAG = "4ed5eb6e5211b129897b7a53b853670f4802d17d8a118092262d078a350ef102"
TEAM_NAME = "harkersystems"

# Services to add. Bypass=True means no audTag (own auth or guest-public).
SERVICES = [
    # Titan-local
    ("posterizarr",   False),
    ("jellyseerr",    True),
    ("dozzle",        False),
    ("pihole",        False),
    ("nextcloud",     False),
    ("forge",         False),
    ("ollama",        False),
    ("nitter",        True),
    ("iptv",          False),
    ("epg",           False),
    ("atlas",         False),
    # Zeus servarr
    ("radarr",        False),
    ("sonarr",        False),
    ("lidarr",        False),
    ("readarr",       False),
    ("prowlarr",      False),
    ("bazarr",        False),
    ("lazylibrarian", False),
    ("overseerr",     True),
    ("tautulli",      False),
    ("qbittorrent",   False),
    ("nzbget",        False),
    ("portainer",     False),
    # Zeus SIEM
    ("copilot",       False),
    ("graylog",       False),
    ("grafana",       False),
    ("wazuh",         False),
    # Zeus OSINT
    ("searxng",       False),
    ("spiderfoot",    False),
    ("nessus",        False),
    # Zeus infra
    ("gitea",         False),
    ("cosmos",        False),
    ("omada",         False),
    ("proxmox",       False),
]


def load_env():
    token = account = None
    with open(ENV_PATH) as f:
        for line in f:
            line = line.strip()
            if line.startswith("CF_API_TOKEN="):
                token = line.split("=", 1)[1].strip("'\"")
            elif line.startswith("CF_ACCOUNT_ID="):
                account = line.split("=", 1)[1].strip("'\"")
    if not token or not account:
        sys.exit("missing CF_API_TOKEN or CF_ACCOUNT_ID in .env.secrets")
    return token, account


def cf_request(method, url, token, body=None):
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return json.loads(body) if body.startswith(("{", "[")) else {"error": body}


def add_cname(token, name):
    url = f"https://api.cloudflare.com/client/v4/zones/{HARKER_ZONE_ID}/dns_records"
    body = {
        "type": "CNAME",
        "name": f"{name}.harker.systems",
        "content": TUNNEL_CNAME,
        "ttl": 1,
        "proxied": True,
        "comment": "added by Caddy gateway plan 2026-04-30",
    }
    return cf_request("POST", url, token, body)


def get_existing_cnames(token):
    url = f"https://api.cloudflare.com/client/v4/zones/{HARKER_ZONE_ID}/dns_records?per_page=100"
    r = cf_request("GET", url, token)
    return {rec["name"]: rec for rec in r.get("result", [])}


def get_tunnel_config(token, account):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account}/cfd_tunnel/{HARKER_TUNNEL_ID}/configurations"
    return cf_request("GET", url, token)


def put_tunnel_config(token, account, config):
    url = f"https://api.cloudflare.com/client/v4/accounts/{account}/cfd_tunnel/{HARKER_TUNNEL_ID}/configurations"
    return cf_request("PUT", url, token, {"config": config})


def build_ingress_rule(name, bypass):
    rule = {
        "hostname": f"{name}.harker.systems",
        "service": CADDY_ORIGIN,
        "originRequest": {},
    }
    if not bypass:
        rule["originRequest"] = {
            "access": {
                "audTag": [AUDTAG],
                "required": True,
                "teamName": TEAM_NAME,
            }
        }
    return rule


def main():
    token, account = load_env()
    print(f"Token len {len(token)}, account ...{account[-4:]}")

    # Step 1: existing CNAME inventory (skip duplicates, never overwrite)
    existing = get_existing_cnames(token)
    print(f"\nExisting harker.systems records: {len(existing)}")
    skip_dns = set()
    for name, _ in SERVICES:
        full = f"{name}.harker.systems"
        if full in existing:
            print(f"  SKIP DNS  {full:35} -> already a {existing[full]['type']}")
            skip_dns.add(name)

    # Step 2: bulk add CNAMEs
    print(f"\nAdding {len(SERVICES) - len(skip_dns)} CNAMEs...")
    added_dns = []
    for name, _ in SERVICES:
        if name in skip_dns:
            continue
        r = add_cname(token, name)
        ok = r.get("success", False)
        if ok:
            added_dns.append(name)
            print(f"  +DNS  {name+'.harker.systems':35}  ok")
        else:
            errs = r.get("errors", [{"message": "unknown"}])
            print(f"  !DNS  {name+'.harker.systems':35}  {errs}")
        time.sleep(0.05)  # rate-limit politeness

    # Step 3: fetch tunnel ingress, splice new rules, PUT
    print("\nFetching tunnel config...")
    cfg = get_tunnel_config(token, account)
    if not cfg.get("success"):
        sys.exit(f"failed to fetch tunnel config: {cfg}")
    config = cfg["result"]["config"]
    ingress = config["ingress"]

    # find existing hostnames in ingress to skip duplicates
    existing_hosts = {r.get("hostname") for r in ingress if "hostname" in r}
    print(f"  current ingress rules: {len(ingress)} (incl catch-all)")

    # build new rules; insert before the http_status:404 catch-all
    new_rules = []
    skipped_ingress = []
    for name, bypass in SERVICES:
        host = f"{name}.harker.systems"
        if host in existing_hosts:
            skipped_ingress.append(name)
            continue
        new_rules.append(build_ingress_rule(name, bypass))

    if skipped_ingress:
        print(f"  SKIP ingress: {', '.join(skipped_ingress)} (already routed)")

    # insert before catch-all (rule with no hostname or http_status:404 service)
    catchall_idx = next(
        (i for i, r in enumerate(ingress) if "hostname" not in r), len(ingress)
    )
    updated_ingress = ingress[:catchall_idx] + new_rules + ingress[catchall_idx:]
    config["ingress"] = updated_ingress

    print(f"\n  inserting {len(new_rules)} new rules at index {catchall_idx}")
    print(f"  new total: {len(updated_ingress)} (was {len(ingress)})")

    # PUT updated config
    print("\nPUT tunnel configuration...")
    r = put_tunnel_config(token, account, config)
    if r.get("success"):
        print(f"  OK — version now {r['result']['version']}")
    else:
        print(f"  FAIL: {r}")
        sys.exit(1)

    # Summary
    print(f"\n=== Summary ===")
    print(f"  CNAMEs added:   {len(added_dns)}")
    print(f"  CNAMEs skipped: {len(skip_dns)}")
    print(f"  Ingress added:  {len(new_rules)}")
    print(f"  Ingress skipped:{len(skipped_ingress)}")
    print(f"\nTunnel config version: {r['result']['version']}")
    print("Propagation typically <60s.")


if __name__ == "__main__":
    main()
