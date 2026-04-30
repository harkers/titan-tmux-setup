#!/usr/bin/env bash
# Start one detached tmux session per /home/stu/projects/ folder on titan.
#
# Run this on titan (or via `ssh titan bash -s` from your Mac). Idempotent:
# any session that already exists is left alone — re-run safely.
#
# Each session is named after its project and starts cd'd into the project
# directory. To attach to one:  tmux a -t <name>
# To list all:                  tmux ls
# To switch between sessions:   prefix + s  (interactive picker)

set -euo pipefail

PROJECTS_DIR="${PROJECTS_DIR:-/home/stu/projects}"

if [ ! -d "$PROJECTS_DIR" ]; then
    echo "no $PROJECTS_DIR — run this on titan" >&2
    exit 1
fi

cd "$PROJECTS_DIR"

# Skip dirs that aren't actual projects (data dumps, symlinks to elsewhere).
SKIP="shield-apks epg"

mapfile -t projects < <(find . -maxdepth 1 -mindepth 1 -type d -printf '%f\n' | sort)

echo "Found ${#projects[@]} candidate folders. Existing sessions:"
tmux ls 2>/dev/null | sed 's/^/  /' || echo "  (none)"
echo

created=0 skipped=0
for p in "${projects[@]}"; do
    case " $SKIP " in
        *" $p "*) echo "  -- $p (in skip list)"; skipped=$((skipped + 1)); continue ;;
    esac

    if tmux has-session -t "$p" 2>/dev/null; then
        echo "  ?? $p (already exists)"
        skipped=$((skipped + 1))
        continue
    fi

    tmux new-session -d -s "$p" -c "$PROJECTS_DIR/$p"
    # Send a status command tuned to what kind of project this is.
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
