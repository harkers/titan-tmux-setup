#!/usr/bin/env bash
# Bootstrap a Linux host with mosh + tmux + this repo's config.
# Tested targets: titan (Debian 12), zeus (Proxmox PVE Debian), nuc, cosmos.
#
# Run modes:
#
#   # First time on a fresh host (stream over SSH):
#   ssh <host> 'bash -s' < ~/projects/tmux-setup/tmux/bootstrap-host.sh
#
#   # After repo is cloned on the host:
#   ssh <host> 'bash ~/tmux-setup/tmux/bootstrap-host.sh'
#
# Env flags:
#   SKIP_SESSIONS=1   don't start tmux sessions, just install + configure
#   REPO_DIR=...      override clone target (default: ~/tmux-setup)
#   REPO_URL=...      override clone URL (default: https://github.com/harkers/tmux-setup.git)

set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/harkers/tmux-setup.git}"
REPO_DIR="${REPO_DIR:-$HOME/tmux-setup}"

# ── sudo wrapper (no-op when running as root, e.g. on Proxmox containers) ──
if [ "$(id -u)" -eq 0 ]; then
    SUDO=""
elif command -v sudo >/dev/null 2>&1; then
    SUDO="sudo"
else
    echo "Need sudo or root for package install." >&2
    exit 1
fi

# ── 1. Install tmux + mosh + fzf + git ──
echo "==> Installing packages"
if command -v apt-get >/dev/null 2>&1; then
    $SUDO apt-get update -qq
    $SUDO apt-get install -y tmux mosh fzf git
elif command -v dnf >/dev/null 2>&1; then
    $SUDO dnf install -y tmux mosh fzf git
elif command -v pacman >/dev/null 2>&1; then
    $SUDO pacman -Sy --noconfirm tmux mosh fzf git
elif command -v apk >/dev/null 2>&1; then
    $SUDO apk add --no-cache tmux mosh fzf git
else
    echo "Unknown package manager — install tmux, mosh, fzf, git manually." >&2
    exit 1
fi

# ── 2. Clone or update the repo ──
if [ -d "$REPO_DIR/.git" ]; then
    echo "==> Updating $REPO_DIR"
    git -C "$REPO_DIR" pull --ff-only
else
    echo "==> Cloning $REPO_URL -> $REPO_DIR"
    git clone "$REPO_URL" "$REPO_DIR"
fi

# ── 3. Symlink ~/.tmux.conf ──
echo "==> Linking ~/.tmux.conf -> $REPO_DIR/tmux/.tmux.conf"
ln -sfn "$REPO_DIR/tmux/.tmux.conf" "$HOME/.tmux.conf"

# ── 4. Install tpm + plugins (tpm clones the rest non-interactively) ──
if [ ! -d "$HOME/.tmux/plugins/tpm" ]; then
    echo "==> Installing tpm"
    git clone --depth 1 https://github.com/tmux-plugins/tpm "$HOME/.tmux/plugins/tpm"
fi
echo "==> Installing tmux plugins"
"$HOME/.tmux/plugins/tpm/bin/install_plugins"

# ── 5. SSH agent socket helper (opt-in via shell rc) ──
# .tmux.conf points panes at $HOME/.ssh/agent.sock. The shell rc snippet below
# keeps that symlink fresh after each SSH login. We APPEND once (marker-guarded).
MARKER="# tmux-setup: stable SSH agent socket"
for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
    [ -f "$rc" ] || continue
    if ! grep -qF "$MARKER" "$rc"; then
        echo "==> Adding SSH agent snippet to $rc"
        cat >> "$rc" <<'EOF'

# tmux-setup: stable SSH agent socket — survives tmux detach/reattach
if [ -n "${SSH_AUTH_SOCK:-}" ] && [ -S "$SSH_AUTH_SOCK" ] && [ "$SSH_AUTH_SOCK" != "$HOME/.ssh/agent.sock" ]; then
    ln -sf "$SSH_AUTH_SOCK" "$HOME/.ssh/agent.sock"
fi
[ -S "$HOME/.ssh/agent.sock" ] && export SSH_AUTH_SOCK="$HOME/.ssh/agent.sock"
EOF
    fi
done

# ── 6. (Optional) start one detached session per ~/projects/*/ ──
if [ "${SKIP_SESSIONS:-}" != "1" ] && [ -d "$HOME/projects" ]; then
    echo "==> Starting sessions"
    PROJECTS_DIR="$HOME/projects" bash "$REPO_DIR/tmux/start-all-sessions.sh" || true
fi

echo
echo "Done on $(hostname). Connect with:"
echo "    mosh $(hostname) -- tmux a"
echo "or:"
echo "    ssh $(hostname); tmux a"
