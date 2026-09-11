#!/usr/bin/env bash
# Guards against qemubox and dockbox diverging on the shared model-alias table
# (the UX most likely to drift). Reads both scripts as text -- the tools stay
# fully independent, with no shared sourced code -- and compares, per alias, the
# model id and effort each maps to.
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
    effort="$(printf '%s' "$line" | grep -oE 'effort (high|xhigh)' | grep -oE 'high|xhigh' | head -1)"
    printf '%s %s' "$model" "$effort"
}

for a in haiku sonnet opus fable gpt mini spark; do
    q="$(alias_spec "$qb" "$a")"
    d="$(alias_spec "$db" "$a")"
    if [ "$q" != "$d" ]; then
        echo "DRIFT: alias '$a' -> qemubox='$q' dockbox='$d'" >&2
        fail=1
    fi
    [ -n "${q// /}" ] || { echo "DRIFT: alias '$a' has no model in qemubox" >&2; fail=1; }
done

# Shared default model (structured differently in each, so checked by presence).
for f in "$qb" "$db"; do
    grep -q 'claude-opus-5 --effort xhigh' "$f" || {
        echo "DRIFT: default 'claude-opus-5 --effort xhigh' missing in $f" >&2; fail=1; }
done

[ "$fail" -eq 0 ] && echo "drift_test.sh: ok"
exit "$fail"
