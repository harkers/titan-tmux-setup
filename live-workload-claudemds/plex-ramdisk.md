# plex-ramdisk on titan

tmpfs/ramdisk setup for Plex hot data — speeds up library walks and transcoding by keeping Plex DB + transcoder cache in RAM.

## Files
- `plan.md` — design document
- `runbook.md` — operational procedures (start, stop, sync to disk)
- `scripts/` — install + maintenance scripts
- `systemd/` — service units that mount/unmount the tmpfs
- `baseline.txt` — performance baseline before ramdisk
- `TODO-cleanup.md` — outstanding work

## Read runbook.md first

There's a specific shutdown order to avoid losing recent Plex DB writes. The systemd units handle the typical case but manual interventions need the runbook.

## Cross-references
- `../plex/` — what consumes the ramdisk
- `../posterizarr/` — `repair_plex_xml.sh` assumes the Plex DB path; ramdisk changes that path
