#!/usr/bin/env bash
# Guards two copies that must stay equal. qemubox and dockbox share the
# model-alias table (the UX most likely to drift): both scripts are read as
# text -- the tools stay fully independent, with no shared sourced code -- and
# compared, per alias (claude is the bare default), on the model id and effort
# each maps to. The writing skill owns the STE language rules and the caveman
# output style carries the same bullets for chat: the two lists are compared.
set -uo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
qb="$root/qemubox/qemubox"
db="$root/dockbox/dockbox"
fail=0

# alias_spec FILE ALIAS -> "model[ effort]" from the alias's code line.
alias_spec() {
    local line model effort
    line="$(grep -E "^[[:space:]]*$2\)" "$1" | grep -E 'claude-|gpt-' | head -1)"
    model="$(printf '%s' "$line" | grep -oE 'claude-[a-z0-9.-]+|gpt-[a-z0-9.-]+' | head -1)"
    effort="$(printf '%s' "$line" | grep -oE 'effort[ =](high|xhigh)' | grep -oE 'high|xhigh' | head -1)"
    printf '%s %s' "$model" "$effort"
}

for a in claude haiku sonnet opus fable codex gpt mini spark; do
    q="$(alias_spec "$qb" "$a")"
    d="$(alias_spec "$db" "$a")"
    if [ "$q" != "$d" ]; then
        echo "DRIFT: alias '$a' -> qemubox='$q' dockbox='$d'" >&2
        fail=1
    fi
    [ -n "${q// /}" ] || { echo "DRIFT: alias '$a' has no model in qemubox" >&2; fail=1; }
done

# language_bullets FILE -> the "- " lines of its "## Language" section.
language_bullets() {
    awk '/^## Language/ {on=1; next} on && /^## / {exit} on && /^- /' "$1"
}

writing="$(language_bullets "$root/skills/writing/SKILL.md")"
caveman="$(language_bullets "$root/output-styles/caveman.md")"
if [ -z "$writing" ] || [ "$writing" != "$caveman" ]; then
    echo "DRIFT: § Language bullets differ between skills/writing/SKILL.md and output-styles/caveman.md" >&2
    diff <(printf '%s\n' "$writing") <(printf '%s\n' "$caveman") >&2
    fail=1
fi

[ "$fail" -eq 0 ] && echo "drift_test.sh: ok"
exit "$fail"
