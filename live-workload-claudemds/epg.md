# EPG server on titan

XMLTV electronic program guide for the IPTV stack. Lives at `/home/stu/epg/` — `/home/stu/projects/epg` is a symlink to it.

## Files
- `start-epg-server.sh` — boot script (started by `@reboot` cron)
- `update-epg.sh` — daily 03:00 cron pulls fresh guide data
- `merge-xmltv.py` — every 15 min, merges sources into a single XMLTV file
- `merge-sport-epg.py` — every 15 min (offset 10), sport-specific merge

## Cron entries (in user crontab, not /etc/cron.d)
```
@reboot              /home/stu/epg/start-epg-server.sh start
0 3 * * *            /home/stu/epg/update-epg.sh
15 * * * *           /usr/bin/python3 /home/stu/projects/epg/merge-xmltv.py
10 * * * *           /usr/bin/python3 /home/stu/projects/epg/merge-sport-epg.py
```

## Common tasks
```bash
# tail current EPG state
tail -f /home/stu/epg/epg-update.log
tail -f /home/stu/projects/epg/merge.log
tail -f /home/stu/projects/epg/merge-sport.log

# manual refresh
/home/stu/epg/update-epg.sh
```

## Cross-references
- `../iptv-blender/` and `../m3u-editor/` consume the EPG output
- `../plex/` displays it via DVR/IPTV channel mapping
