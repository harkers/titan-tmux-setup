# plex-overlay on titan

Pure-Python bulk overlay tool that replaces Kometa overlay-application phase. v1.0 deployed 2026-04-29. Target: full 15K movie library in <50 min (was 30+h with Kometa).

## Architecture
- 7 modules: cli, config, plex, state, classifier, renderer, pipeline
- Pillow PIL compositor with text/ribbon/image dispatch
- asyncio.Queue producer/consumer (compose ↔ upload pipelined)
- multiprocessing.Pool with warm_worker initializer
- SQLite + fcntl FileLock for concurrent state

## Files
- `pyproject.toml` — packaging
- `plex_overlay/` — main package
- `config.yml` — runtime config (token, paths, libraries)
- `scripts/sync_ribbon_labels.py` — weekly IMDb Top 250 / Oscar refresh (cron Sun 03:00)
- `state/` — SQLite + locks
- `tests/` — 85 passing
- `docs/superpowers/specs/2026-04-29-plex-overlay-tool-design.md` — spec
- `docs/superpowers/plans/2026-04-29-plex-overlay-v1-build.md` — build plan

## Common tasks
```bash
python -m plex_overlay --library "Movies" --workers 4
python -m plex_overlay --status
tail -f state/run.log
pytest
```

## Performance notes
- Pre-flight benchmark measured 8.8 POSTs/sec at concurrency 4
- Pillow-SIMD only available <10.x, fell back to stock Pillow
- Cross-platform snapshot byte-diffs: Mac Pillow 12 vs Linux Pillow 11 produce different JPEG bytes; snapshots regenerated on titan

## Cross-references
- `../posterizarr/` — base poster source; once first-run finishes, point posterizarr_asset_dir there
- `../kometa/` — overlay phase replaced by this
- `../plex/` — target server
