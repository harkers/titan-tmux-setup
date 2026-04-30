# Bootstrap scripts

One-shot scripts that did the original `*.harker.systems` rollout on **2026-04-30**. All four are idempotent (skip-if-exists) — re-running them is safe but unnecessary on an already-bootstrapped account.

| # | File | What it did |
|---|---|---|
| 01 | [`01_add_harker_services.py`](01_add_harker_services.py) | Added 34 CNAMEs + 34 tunnel ingress rules (28 gated, 4 bypass + ssh) |
| 02 | [`02_create_access_app.py`](02_create_access_app.py) | Created the `Harker Systems Homelab` Access app for `*.harker.systems` |
| 03 | [`03_expand_audtags.py`](03_expand_audtags.py) | Expanded audTag list on every `*.harker.systems` ingress rule to include both old (Dashboard, `*.teamharker.com`) and new (Homelab) audTags so existing sessions keep working |
| 04 | [`04_add_ssh_breakglass.py`](04_add_ssh_breakglass.py) | Added `ssh.harker.systems → ssh://192.168.10.80:22` for cloudflared SSH break-glass |

## When to re-run

Almost never. Use the daily-driver scripts in the parent folder for normal additions:

- [`../add_service.py`](../add_service.py) — add one new hostname
- [`../list_services.py`](../list_services.py) — see what's currently routed
- [`../remove_service.py`](../remove_service.py) — remove one hostname

If you ever blow away the account state (e.g. tunnel was deleted and recreated), run these in order: 01 → 02 → 03 → 04. The CNAME records in DNS point at the tunnel UUID, so a fresh tunnel needs the IDs in [`../cf_common.py`](../cf_common.py) updated first.

## Capturing context (audit log)

Run `python3 ../list_services.py > services.txt` to snapshot the current routing table, useful for change reviews or restoring after an accidental delete.
