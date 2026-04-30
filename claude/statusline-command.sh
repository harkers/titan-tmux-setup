#!/bin/sh
input=$(cat)

host=$(hostname -s)
dir=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
model=$(echo "$input" | jq -r '.model.display_name // ""')
used=$(echo "$input" | jq -r '.context_window.used_percentage // empty')

# Collapse $HOME to ~
home=$(echo "$HOME" | sed 's|/*$||')
case "$dir" in
  "$home"/*)  dir_display="~${dir#$home}" ;;
  *)          dir_display="$dir" ;;
esac

# Extract project name: folder directly under Projects/ or projects/
project=$(echo "$dir" | sed -n 's|.*/[Pp]rojects/\([^/]*\).*|\1|p')

# Build context segment
ctx=""
if [ -n "$used" ]; then
  ctx=$(printf " ctx:%.0f%%" "$used")
fi

# Build status line
if [ -n "$project" ]; then
  printf "\033[2m[%s]\033[0m \033[2m%s\033[0m  \033[2m%s%s\033[0m" \
    "$project" "$dir_display" "$model" "$ctx"
else
  printf "\033[2m%s\033[0m  \033[2m%s%s\033[0m" \
    "$dir_display" "$model" "$ctx"
fi
