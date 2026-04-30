#!/usr/bin/env bash
# Start one detached tmux session per project folder.
# Idempotent: any session that already exists is left alone.
#
# Portable across:
#   Mac default bash 3.2 (no mapfile)
#   BSD find (no -printf)
#   Linux/GNU bash + find
#
# Env vars:
#   PROJECTS_DIR     directory whose subfolders become sessions
#                    default: /home/stu/projects (titan layout)
#                    on Mac:  set to ~/Projects
#   PROJECTS_FILTER  space-separated allowlist of session names. Only
#                    these will be created. Empty = all subfolders.
#                    Useful on Mac where ~/Projects has many things
#                    but only some are sessions you want.
#   SKIP             space-separated denylist (default 'shield-apks')
#
# Examples:
#   # titan: all of /home/stu/projects/, skipping shield-apks
#   bash start-all-sessions.sh
#
#   # mac: only the four named projects under ~/Projects
#   PROJECTS_DIR=~/Projects \
#     PROJECTS_FILTER='ordered-edge fidelex orderededge-agents py-plex' \
#     bash start-all-sessions.sh

set -o pipefail
# (deliberately no `set -u` — bash 3.2 on macOS fights -u when expanding
# an empty array. We're careful with quoting instead.)

PROJECTS_DIR="${PROJECTS_DIR:-/home/stu/projects}"
PROJECTS_FILTER="${PROJECTS_FILTER:-}"
SKIP="${SKIP:-shield-apks}"

if [ ! -d "$PROJECTS_DIR" ]; then
    echo "no $PROJECTS_DIR — set PROJECTS_DIR or run on titan" >&2
    exit 1
fi

# Build the list of project names to consider — portable on bash 3.2 + BSD.
projects=()
for d in "$PROJECTS_DIR"/*/; do
    [ -d "$d" ] || continue
    name="${d%/}"
    name="${name##*/}"

    # apply allowlist if set
    if [ -n "$PROJECTS_FILTER" ]; then
        case " $PROJECTS_FILTER " in
            *" $name "*) ;;
            *) continue ;;
        esac
    fi

    # apply denylist
    case " $SKIP " in
        *" $name "*) continue ;;
    esac

    projects+=("$name")
done

# Sort for stable output (skip if empty — bash 3.2 + set -u trap)
if [ "${#projects[@]}" -gt 0 ]; then
    IFS=$'\n' projects=($(printf '%s\n' "${projects[@]}" | sort))
    unset IFS
fi

echo "Found ${#projects[@]} candidate folders in $PROJECTS_DIR. Existing sessions:"
tmux ls 2>/dev/null | sed 's/^/  /' || echo "  (none)"
echo

created=0
skipped=0
for p in "${projects[@]}"; do
    if tmux has-session -t "$p" 2>/dev/null; then
        echo "  ?? $p (already exists)"
        skipped=$((skipped + 1))
        continue
    fi

    tmux new-session -d -s "$p" -c "$PROJECTS_DIR/$p"
    # Pick an intro command that makes sense for the project type
    if [ -d "$PROJECTS_DIR/$p/.git" ]; then
        tmux send-keys -t "$p" 'git status -sb 2>/dev/null | head -20' Enter
    elif [ -f "$PROJECTS_DIR/$p/docker-compose.yml" ]; then
        tmux send-keys -t "$p" 'docker compose ps 2>/dev/null' Enter
    else
        tmux send-keys -t "$p" 'ls -la' Enter
    fi
    echo "  ++ $p"
    created=$((created + 1))
done

echo
echo "Done — created $created, skipped $skipped."
echo
echo "Sessions now running:"
tmux ls | sed 's/^/  /'
echo
echo "Attach to one:    tmux a -t <name>"
echo "Switch between:   inside tmux, prefix + s for interactive picker"
echo "Detach:           prefix + d"
echo "Kill all (later): tmux kill-server"
