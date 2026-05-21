#!/usr/bin/env bash
# Mac entrypoint for start-all-sessions.sh.
# Used by the LaunchAgent at ~/Library/LaunchAgents/dev.harkers.tmux-sessions.plist.
# Adds Homebrew to PATH (LaunchAgents inherit a minimal env) and points at ~/projects.

set -o pipefail

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"

PROJECTS_DIR="$HOME/projects" \
    bash "$HOME/projects/tmux-setup/tmux/start-all-sessions.sh"
