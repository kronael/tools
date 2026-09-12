#!/usr/bin/env bash
# Ask a model a question with no access to this machine's guidance: a throwaway
# HOME so no wisdom file exists to load, and an empty working directory so no
# project CLAUDE.md is discoverable. Prints the model's answer and nothing else.
#
# usage: minimize/scripts/clean-room.sh <model> <prompt-file>
# needs: CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY exported by the caller.
set -euo pipefail

model=${1:?usage: minimize/scripts/clean-room.sh <model> <prompt-file>}
prompt_file=${2:?usage: minimize/scripts/clean-room.sh <model> <prompt-file>}

if [ -z "${CLAUDE_CODE_OAUTH_TOKEN:-}${ANTHROPIC_API_KEY:-}" ]; then
    echo "clean-room.sh: export CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY first" >&2
    exit 1
fi

room=$(mktemp -d)
trap 'find "$room" -type f -delete; find "$room" -depth -type d -exec rmdir {} +' EXIT
mkdir -p "$room/home" "$room/cwd"

cd "$room/cwd"
env -i \
    HOME="$room/home" \
    PATH="$PATH" \
    TERM=dumb \
    CLAUDE_CODE_OAUTH_TOKEN="${CLAUDE_CODE_OAUTH_TOKEN:-}" \
    ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
    claude -p --model "$model" "$(cat "$prompt_file")" < /dev/null
