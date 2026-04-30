#!/usr/bin/env python3
"""Remove a service hostname from harker.systems.

Deletes the CNAME and the tunnel ingress rule. Idempotent.

Usage:
    python3 remove_service.py <subdomain>
"""
from __future__ import annotations

import argparse

from cf_common import (
    HARKER_ZONE_ID,
    cf,
    load_env,
    tunnel_config,
    zone,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("subdomain")
    args = parser.parse_args()
    full = f"{args.subdomain}.harker.systems"

    token, account = load_env()

    # 1. Remove CNAME
    r = cf("GET", zone(HARKER_ZONE_ID, f"dns_records?name={full}"), token)
    for rec in r.get("result", []) or []:
        rid = rec["id"]
        del_r = cf("DELETE", zone(HARKER_ZONE_ID, f"dns_records/{rid}"), token)
        ok = "OK" if del_r.get("success") else f"FAIL {del_r.get('errors')}"
        print(f"  - DNS {full} ({rec['type']}) {ok}")
    if not r.get("result"):
        print(f"  no DNS record for {full}")

    # 2. Remove tunnel ingress rule
    cfg = cf("GET", tunnel_config(account), token)
    config = cfg["result"]["config"]
    before = len(config["ingress"])
    config["ingress"] = [
        rule for rule in config["ingress"] if rule.get("hostname") != full
    ]
    after = len(config["ingress"])
    if before == after:
        print(f"  no ingress rule for {full}")
        return 0
    pr = cf("PUT", tunnel_config(account), token, {"config": config})
    if pr.get("success"):
        print(f"  - ingress {full} removed (tunnel v{pr['result']['version']})")
    else:
        print(f"  ingress remove FAILED: {pr.get('errors')}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
