#!/usr/bin/env python3
"""Try creating a new wildcard *.harker.systems Access app.

If the token can create but not patch, this is the workaround.
Falls back to printing dashboard instructions if it can't.
"""
import json
import sys
import urllib.request
import urllib.error

ENV_PATH = "/Users/stu/Projects/ordered-edge/.env.secrets"


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
    base = f"https://api.cloudflare.com/client/v4/accounts/{account}/access/apps"

    # First check: is there an existing policy we can clone?
    apps = cf("GET", f"{base}?per_page=50", token)
    dash = next(
        (a for a in apps["result"] if a.get("name") == "Dashboard"),
        None,
    )
    if not dash:
        print("Dashboard app not found")
        sys.exit(1)

    # Get its policy
    pol_url = f"{base}/{dash['id']}/policies"
    pols = cf("GET", pol_url, token)
    if not pols.get("success"):
        print("can't read Dashboard policies:", pols.get("errors"))

    # Build new app
    body = {
        "name": "Harker Systems Homelab",
        "domain": "*.harker.systems",
        "type": "self_hosted",
        "session_duration": "24h",
        "app_launcher_visible": True,
        "self_hosted_domains": ["*.harker.systems"],
    }
    print("attempting POST /access/apps with body:", json.dumps(body, indent=2))
    r = cf("POST", base, token, body)
    print("success:", r.get("success"))
    if not r.get("success"):
        print("errors:", json.dumps(r.get("errors"), indent=2))
        return
    new_app = r["result"]
    print("new app id:", new_app["id"])
    print("new app aud:", new_app.get("aud"))

    # Add the same policy as Dashboard if we got one
    if pols.get("success") and pols.get("result"):
        first_pol = pols["result"][0]
        new_pol_body = {
            "name": first_pol.get("name", "Permitted principals"),
            "decision": first_pol.get("decision", "allow"),
            "include": first_pol.get("include", []),
            "require": first_pol.get("require", []),
            "exclude": first_pol.get("exclude", []),
            "session_duration": first_pol.get("session_duration", "24h"),
        }
        pr = cf("POST", f"{base}/{new_app['id']}/policies", token, new_pol_body)
        print("policy create success:", pr.get("success"))
        if not pr.get("success"):
            print("policy errors:", pr.get("errors"))


if __name__ == "__main__":
    main()
