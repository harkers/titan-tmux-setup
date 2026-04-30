#!/usr/bin/env python3
"""List all *.harker.systems services routed by the harker.systems tunnel.

Shows hostname, backend, and whether CF Access auth is enforced.
"""
from cf_common import cf, load_env, tunnel_config


def main() -> None:
    token, account = load_env()
    cfg = cf("GET", tunnel_config(account), token)
    ingress = cfg["result"]["config"]["ingress"]

    rules = [r for r in ingress if r.get("hostname")]
    rules.sort(key=lambda r: r["hostname"])
    print(f"{len(rules)} hostnames routed by harker.systems tunnel:")
    print(f"  tunnel config version: {cfg['result']['version']}\n")
    print(f"  {'HOSTNAME':40} {'AUTH':8} BACKEND")
    for r in rules:
        host = r["hostname"]
        backend = r.get("service", "?")
        access = r.get("originRequest", {}).get("access") or {}
        auth = "GATED" if access.get("required") else "open"
        print(f"  {host:40} {auth:8} {backend}")


if __name__ == "__main__":
    main()
