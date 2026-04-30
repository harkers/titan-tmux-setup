# shield-apks on titan

Storage for nVidia SHIELD Android TV APK files (Plex client builds, sideloaded apps).

## Use
- ADB sideload onto SHIELD: `adb -s 192.168.10.128:5555 install <apk>`
- Backup of versions that work — when an upstream Plex update breaks something, roll back from here

## Cross-references
- See [memory: SHIELD plex.tv quality preset bug](file:///Users/stu/.claude/projects/-Users-stu-plex/memory/) — broken 200 kbps preset survives app data clear
- See [memory: SHIELD NordVPN split-tunnel](file:///Users/stu/.claude/projects/-Users-stu-plex/memory/) — Plex (UID 10089) split-tunnel config

This is data, not a project — no docker/python/git here.
