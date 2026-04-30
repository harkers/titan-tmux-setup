#!/usr/bin/env bash
# Rebuild the British Cinema static site and deploy it to /var/www/british-cinema/.
#
# Build pipeline lives at /home/stu/projects/kometa/posters/ — this script
# is purely the wrapper that runs build_site.py and rsyncs the output.

set -euo pipefail

POSTERS_DIR="/home/stu/projects/kometa/posters"
SITE_SRC="${POSTERS_DIR}/site"
DEPLOY_DST="/var/www/british-cinema"

if [ ! -d "$POSTERS_DIR" ]; then
    echo "ERR: $POSTERS_DIR not found — Kometa posters source missing" >&2
    exit 1
fi

if [ ! -d "$DEPLOY_DST" ]; then
    echo "ERR: $DEPLOY_DST does not exist — would create empty deploy" >&2
    exit 1
fi

echo "[$(date -Is)] Building site from $POSTERS_DIR..."
cd "$POSTERS_DIR"
python3 build_site.py

if [ ! -d "$SITE_SRC" ]; then
    echo "ERR: $SITE_SRC not produced by build_site.py" >&2
    exit 1
fi

echo "[$(date -Is)] Deploying $SITE_SRC -> $DEPLOY_DST..."
sudo rsync -a --delete "${SITE_SRC}/" "${DEPLOY_DST}/"

echo "[$(date -Is)] Done."
echo
echo "Verify:"
echo "  ls $DEPLOY_DST/"
echo "  curl -sI https://titan.tail1a2109.ts.net/british-cinema/ | head -3"
