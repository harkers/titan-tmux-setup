#!/usr/bin/env bash
# Quick status: last deploy time, served paths, file counts.

DEPLOY_DST="/var/www/british-cinema"
POSTERS_SITE="/home/stu/projects/kometa/posters/site"

echo "=== Last deploy ==="
if [ -f "$DEPLOY_DST/index.html" ]; then
    sudo stat -c "  modified: %y" "$DEPLOY_DST/index.html"
    sudo du -sh "$DEPLOY_DST" | sed "s|^|  size:     |"
else
    echo "  (no $DEPLOY_DST yet — first deploy needed)"
fi

echo
echo "=== Staging output ==="
if [ -d "$POSTERS_SITE" ]; then
    stat -c "  modified: %y" "$POSTERS_SITE"
    du -sh "$POSTERS_SITE" | sed "s|^|  size:     |"
else
    echo "  (no $POSTERS_SITE — run build_site.py first)"
fi

echo
echo "=== Tailscale serve config ==="
tailscale serve status 2>&1 | sed "s|^|  |"

echo
echo "=== Quick HTTP probe ==="
curl -sI --max-time 5 https://titan.tail1a2109.ts.net/british-cinema/ 2>&1 | head -3 | sed "s|^|  |"

echo
echo "=== File counts (deployed) ==="
if [ -d "$DEPLOY_DST" ]; then
    for sub in actors directors studios themes tv awards; do
        if [ -d "$DEPLOY_DST/$sub" ]; then
            n=$(find "$DEPLOY_DST/$sub" -name "*.html" 2>/dev/null | wc -l)
            printf "  %-12s %s pages\n" "$sub" "$n"
        fi
    done
fi
