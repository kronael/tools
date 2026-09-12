#!/usr/bin/env bash
# Ask a model a question with no access to this machine's guidance: a throwaway
# HOME so no wisdom file exists to load, and an empty working directory so no
# project CLAUDE.md is discoverable. Prints the model's answer on stdout and
# nothing else; any failure exits non-zero with the reason on stderr.
#
# usage: clean-room.sh <model> <prompt-file>
# needs: CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY exported by the caller.
set -euo pipefail

model=${1:?usage: clean-room.sh <model> <prompt-file>}
prompt_file=${2:?usage: clean-room.sh <model> <prompt-file>}

if [ -z "${CLAUDE_CODE_OAUTH_TOKEN:-}${ANTHROPIC_API_KEY:-}" ]; then
    echo "clean-room.sh: export CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY first" >&2
    exit 1
fi
[ -s "$prompt_file" ] || { echo "clean-room.sh: no prompt in $prompt_file" >&2; exit 1; }

# TMPDIR is pinned: a room under a project tree would inherit that tree's CLAUDE.md.
room=$(TMPDIR=/tmp mktemp -d)
trap 'find "$room" \! -type d -delete; find "$room" -depth -type d -exec rmdir {} +' EXIT
mkdir -p "$room/home" "$room/cwd"

prompt=$(cat "$prompt_file")
cd "$room/cwd"
set +e
answer=$(env -i \
    HOME="$room/home" \
    PATH="$PATH" \
    TERM=dumb \
    CLAUDE_CODE_OAUTH_TOKEN="${CLAUDE_CODE_OAUTH_TOKEN:-}" \
    ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
    claude -p --model "$model" "$prompt" < /dev/null 2> "$room/err")
rc=$?
set -e

# An unrecognized model answers from whatever the CLI resolves instead, which
# silently turns a two-model verdict into one model run twice.
if grep -q unrecognized_model "$room/err"; then
    echo "clean-room.sh: '$model' is not a known model" >&2
    exit 1
fi
[ "$rc" -eq 0 ] || { echo "clean-room.sh: claude exited $rc" >&2; cat "$room/err" >&2; exit "$rc"; }
[ -n "$answer" ] || { echo "clean-room.sh: empty answer from $model" >&2; exit 1; }

printf '%s\n' "$answer"
