#!/bin/bash
# Nudge commit every 100 tool calls OR 10 minutes — non-blocking.
STATE_DIR="${HOME}/.claude/tmp"
mkdir -p "$STATE_DIR"
STATE_FILE="$STATE_DIR/commit-nudge"
read -r ts cnt < "$STATE_FILE" 2>/dev/null || { ts=$(date +%s); cnt=0; }
[[ "$ts" =~ ^[0-9]+$ ]] || ts=$(date +%s)
[[ "$cnt" =~ ^[0-9]+$ ]] || cnt=0

cnt=$((cnt + 1))
now=$(date +%s)

if (( now - ts >= 600 )) || (( cnt >= 100 )); then
    printf '%s 0\n' "$now" > "$STATE_FILE"
    python3 ~/.claude/hooks/stop.py 2>&1 || true
else
    printf '%s %s\n' "$ts" "$cnt" > "$STATE_FILE"
fi

exit 0
