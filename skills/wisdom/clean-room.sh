#!/usr/bin/env bash
# Ask a model that sees none of this machine's guidance, then prove it from the
# run's own transcript.
#
# usage: clean-room.sh <model-id> <prompt-file>  run in a fresh room, then check
#        clean-room.sh check <model-id> <room>   check an existing room
#
# <model-id> is a full ID such as claude-opus-5-5: the check compares it
# verbatim with the model of every assistant record. A run needs
# CLAUDE_CODE_OAUTH_TOKEN or ANTHROPIC_API_KEY exported. The room stays under
# /var/tmp, since removing it is recursive. Exits non-zero when the run or the
# check fails.
set -Eeuo pipefail

check() {
    local model=$1 room=$2
    local logs result
    mapfile -t logs < <(
        find "$room/home/.claude/projects" -name '*.jsonl' 2>/dev/null
    )
    if (( ${#logs[@]} == 0 ))
    then
        echo "check: no transcript under $room/home/.claude/projects" >&2
        return 1
    fi
    result=$(jq -rs --arg model "$model" '
        def attached(kind):
            [.[] | select(.type == "attachment" and .attachment.type == kind)]
            | length;
        [.[] | select(.type == "assistant")] as $said
        | {
            skill_listing: attached("skill_listing"),
            instructions: attached("instructions"),
            nested_memory: attached("nested_memory"),
            tool_use: [$said[] | .message.content
                | if type == "array" then .[] else empty end
                | select(.type == "tool_use")] | length,
            assistant: $said | length,
            off_model: [$said[] | .message.model | select(. != $model)] | unique
          }
        | .pass = (.skill_listing + .instructions + .nested_memory
            + .tool_use == 0 and .assistant > 0 and (.off_model | length) == 0)
        | to_entries[] | "check: \(.key) \(.value | tojson)"
    ' "${logs[@]}")
    echo "$result" >&2
    grep -qx 'check: pass true' <<<"$result"
}

run() {
    local model=$1 prompt_file=$2
    local prompt bin room
    local status=0
    prompt=$(<"$prompt_file")
    bin=$(command -v claude)
    room=$(mktemp -d -p /var/tmp cleanroom-XXXXXX)
    mkdir -p "$room/home/.claude" "$room/cwd"
    echo "room: $room" >&2
    cd "$room/cwd"
    env -i HOME="$room/home" CLAUDE_CONFIG_DIR="$room/home/.claude" \
        PATH="/usr/bin:/bin:${bin%/*}" TERM=dumb \
        CLAUDE_CODE_OAUTH_TOKEN="${CLAUDE_CODE_OAUTH_TOKEN:-}" \
        ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
        claude -p --tools "" --safe-mode --disable-slash-commands \
        --model "$model" "$prompt" < /dev/null || status=$?
    check "$model" "$room" || status=1
    return "$status"
}

case ${1:-} in
check)
    check "${2:?usage: clean-room.sh check <model-id> <room>}" "${3:?room}"
    ;;
*)
    run "${1:?usage: clean-room.sh <model-id> <prompt-file>}" \
        "${2:?prompt-file}"
    ;;
esac
