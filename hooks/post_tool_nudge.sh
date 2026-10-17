#!/bin/bash
# PostToolUse: reflow a written Markdown file, then nudge commit every 100 tool
# calls OR 10 minutes — non-blocking.
PAYLOAD=$(cat)

# pretool_nudge.py reflows the .md a write tool touched when its repository
# opted in; the glob spares every other call the Python start-up. Its note is
# this call's whole output: two JSON documents on stdout parse as none.
if [[ "$PAYLOAD" == *.[mM][dD]\"* ]]; then
    NOTE=$(printf '%s\n' "$PAYLOAD" | python3 ~/.claude/hooks/pretool_nudge.py 2>/dev/null)
    if [[ -n "$NOTE" ]]; then
        printf '%s\n' "$NOTE"
        exit 0
    fi
fi

GIT_DIR=$(git rev-parse --git-dir 2>/dev/null) || exit 0
case "$GIT_DIR" in
    /*) STATE_FILE="$GIT_DIR/post_tool_nudge" ;;
    *) STATE_FILE="${PWD}/${GIT_DIR}/post_tool_nudge" ;;
esac
: 2>/dev/null >> "$STATE_FILE" || exit 0
read -r ts cnt < "$STATE_FILE" 2>/dev/null || { ts=$(date +%s); cnt=0; }
[[ "$ts" =~ ^[0-9]+$ ]] || ts=$(date +%s)
[[ "$cnt" =~ ^[0-9]+$ ]] || cnt=0

cnt=$((cnt + 1))
now=$(date +%s)

if (( now - ts >= 600 )) || (( cnt >= 100 )); then
    printf '%s 0\n' "$now" > "$STATE_FILE"
    printf '%s\n' "$PAYLOAD" \
        | KRONAEL_HOOK_EVENT=PostToolUse python3 ~/.claude/hooks/stop.py 2>/dev/null \
        || true
else
    printf '%s %s\n' "$ts" "$cnt" > "$STATE_FILE"
fi

exit 0
