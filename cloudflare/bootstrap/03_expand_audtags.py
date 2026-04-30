#!/usr/bin/env python3
"""Update harker.systems tunnel ingress rules to include both audTags.

For every rule whose hostname ends with `.harker.systems` and has an
existing access block (audTag enforcement), expand the audTag list to
include both the old Dashboard audTag and the new harker.systems app's
audTag. Bypass services (no access block) are left untouched.
"""
import json
import sys
import urllib.request
import urllib.error

ENV_PATH = "/Users/stu/Projects/ordered-edge/.env.secrets"
TUNNEL_ID = "8ba2b285-f8c1-464b-914e-f758c48d9e04"

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


def main():
    token, account = load_env()
    cfg_url = (
        f"https://api.cloudflare.com/client/v4/accounts/{account}"
        f"/cfd_tunnel/{TUNNEL_ID}/configurations"
    )
    cfg = cf("GET", cfg_url, token)
    config = cfg["result"]["config"]
    ingress = config["ingress"]

    updated = 0
    for rule in ingress:
        host = rule.get("hostname", "")
        if not host.endswith(".harker.systems"):
            continue
        access = rule.get("originRequest", {}).get("access")
        if not access or not access.get("required"):
            continue  # bypass / no auth — skip
        existing = set(access.get("audTag") or [])
        wanted = existing | {OLD_AUD, NEW_AUD}
        if wanted == existing:
            continue  # already has both
        access["audTag"] = sorted(wanted)
        updated += 1
        print(f"  + {host:35} audTag now {len(access['audTag'])} entries")

    if updated == 0:
        print("nothing to update")
        return

    print(f"\nPUT updated config — {updated} rules modified...")
    r = cf("PUT", cfg_url, token, {"config": config})
    print("success:", r.get("success"))
    if not r.get("success"):
        print("errors:", json.dumps(r.get("errors"), indent=2))
        sys.exit(1)
    print("version now:", r["result"]["version"])


if __name__ == "__main__":
    main()
