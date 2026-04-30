#!/usr/bin/env python3
"""Add a single new service hostname under harker.systems.

Creates the CNAME and the tunnel ingress rule (with optional audTag
gate). All rules route to Caddy on titan; Caddy fans out by Host header.

Usage:
    python3 add_service.py <subdomain> [--bypass]

Examples:
    python3 add_service.py radarr            # gated by CF Access
    python3 add_service.py overseerr --bypass  # no auth (guest-public)

Idempotent: re-running for a subdomain that already has a CNAME or
ingress rule will skip those steps.
"""
from __future__ import annotations

import argparse
import sys

from cf_common import (
    CADDY_ORIGIN,
    DEFAULT_AUDTAGS,
    HARKER_TUNNEL_ID,
    HARKER_ZONE_ID,
    TEAM_NAME,
    TUNNEL_CNAME,
    cf,
    load_env,
    tunnel_config,
    zone,
)


def add_cname(token: str, name: str) -> bool:
    full = f"{name}.harker.systems"
    existing = cf("GET", zone(HARKER_ZONE_ID, f"dns_records?name={full}"), token)
    if existing.get("result"):
        print(f"  CNAME {full} already exists — skip")
        return True
    body = {
        "type": "CNAME",
        "name": full,
        "content": TUNNEL_CNAME,
        "ttl": 1,
        "proxied": True,
        "comment": "added via cloudflare/add_service.py",
    }
    r = cf("POST", zone(HARKER_ZONE_ID, "dns_records"), token, body)
    if r.get("success"):
        print(f"  + CNAME {full}")
        return True
    print(f"  ! CNAME {full} FAILED: {r.get('errors')}")
    return False


def add_ingress(token: str, account: str, name: str, bypass: bool) -> bool:
    cfg = cf("GET", tunnel_config(account), token)
    config = cfg["result"]["config"]
    ingress = config["ingress"]

    full = f"{name}.harker.systems"
    if any(r.get("hostname") == full for r in ingress):
        print(f"  ingress {full} already routed — skip")
        return True

    rule: dict = {
        "hostname": full,
        "service": CADDY_ORIGIN,
        "originRequest": {},
    }
    if not bypass:
        rule["originRequest"] = {
            "access": {
                "audTag": list(DEFAULT_AUDTAGS),
                "required": True,
                "teamName": TEAM_NAME,
            }
        }

    catchall_idx = next(
        (i for i, r in enumerate(ingress) if "hostname" not in r), len(ingress)
    )
    ingress.insert(catchall_idx, rule)
    config["ingress"] = ingress

    r = cf("PUT", tunnel_config(account), token, {"config": config})
    if r.get("success"):
        flag = "BYPASS" if bypass else "GATED"
        v = r["result"]["version"]
        print(f"  + ingress {full} ({flag}) — tunnel config v{v}")
        return True
    print(f"  ! ingress {full} FAILED: {r.get('errors')}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("subdomain", help="e.g. radarr (just the subdomain part)")
    parser.add_argument(
        "--bypass",
        action="store_true",
        help="don't gate with CF Access (use for guest-public services)",
    )
    args = parser.parse_args()

    if "." in args.subdomain or args.subdomain.startswith("-"):
        sys.exit(f"give just the subdomain, not a full hostname: {args.subdomain}")

    token, account = load_env()
    print(f"Adding {args.subdomain}.harker.systems "
          f"({'BYPASS' if args.bypass else 'GATED with CF Access'}):")
    if not add_cname(token, args.subdomain):
        return 1
    if not add_ingress(token, account, args.subdomain, args.bypass):
        return 1
    print("\nNext: add the corresponding site block to caddy/Caddyfile and reload.")
    print(f"  http://{args.subdomain}.harker.systems {{")
    print("      reverse_proxy <backend host:port> {")
    print("          lb_try_duration 4s")
    print("          transport http { dial_timeout 8s }")
    print("      }")
    print("  }")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
