#!/usr/bin/env bash
# Ask a model with none of this machine's guidance visible: a throwaway HOME so
# no wisdom file loads, an empty cwd so no project CLAUDE.md is discoverable.
# The room is left behind — cleaning it needs recursive removal, which is banned.
#
# usage: clean-room.sh <model> <prompt-file>
# needs: CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY exported by the caller.
set -euo pipefail

room=$(TMPDIR=/tmp mktemp -d)
mkdir -p "$room/home" "$room/cwd"
prompt=$(cat "$2")

cd "$room/cwd"
env -i HOME="$room/home" PATH="$PATH" TERM=dumb \
    CLAUDE_CODE_OAUTH_TOKEN="${CLAUDE_CODE_OAUTH_TOKEN:-}" \
    ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
    claude -p --model "$1" "$prompt" < /dev/null
