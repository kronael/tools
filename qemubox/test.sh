#!/usr/bin/env bash
# Unit tests for qemubox's pure helpers. Sources the script with QEMUBOX_LIB=1
# so the CLI never runs and no VM is booted; asserts the security-load-bearing
# behavior (name guard, rm matcher, -v path parse, port derivation, and the
# per-flag 9p mount matrix).
set -uo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
fixture="$(mktemp -d)"
trap 'rm -rf "$fixture"' EXIT

# Fixture home holding the agent-config dirs assemble_mounts probes for.
export HOME="$fixture/home"
export QEMUBOX_HOME="$fixture/state"
mkdir -p "$HOME/.claude" "$HOME/.codex" "$HOME/.agents" "$QEMUBOX_HOME"
PROJ="$fixture/proj"; mkdir -p "$PROJ"

# shellcheck disable=SC1090
QEMUBOX_LIB=1 . "$here/qemubox"
set +e  # sourcing turned on set -e; take back control for assertions

pass=0; fail=0
ok()   { pass=$((pass+1)); }
bad()  { fail=$((fail+1)); echo "FAIL: $1" >&2; }
eq()   { [ "$2" = "$3" ] && ok || bad "$1: expected '$3' got '$2'"; }
true_() { if eval "$2"; then ok; else bad "$1"; fi; }
false_(){ if eval "$2"; then bad "$1"; else ok; fi; }

# exits with code $1 when run in a subshell? (guards use exit, so run isolated)
exits() { ( eval "$2" ) >/dev/null 2>&1; [ "$?" = "$1" ] && ok || bad "$3"; }

## box_name -----------------------------------------------------------------
eq "box_name plain" "$(box_name repo)" "repo"
eq "box_name slash->dash" "$(box_name a/b)" "a-b"
eq "box_name default" "$(box_name)" "default"

## rm_matches ---------------------------------------------------------------
true_  "rm empty pattern matches all"        'rm_matches anything ""'
true_  "rm exact match"                      'rm_matches staking-rewards staking-rewards'
false_ "rm exact does not substring-match"   'rm_matches staking-rewards-facade staking-rewards'
true_  "rm glob star"                        'rm_matches repo-1 "repo-*"'
false_ "rm glob non-match"                   'rm_matches other "repo-*"'

## copy_arg -----------------------------------------------------------------
eq "copy_arg abs"        "$(copy_arg /a/b)" "/a/b"
eq "copy_arg strip :rw"  "$(copy_arg /a/b:rw)" "/a/b"
eq "copy_arg strip :ro"  "$(copy_arg /a/b:ro)" "/a/b"
eq "copy_arg keep inner colon" "$(copy_arg /a:b:rw)" "/a:b"
exits 2 'copy_arg rel' "copy_arg rejects relative path"

## -n traversal guard ------------------------------------------------------
exits 2 'apply_flag n ..'       "-n .. rejected"
exits 2 'apply_flag n .'        "-n . rejected"
exits 2 'apply_flag n base'     "-n base rejected"
exits 2 'apply_flag n ""'       "-n empty rejected"
exits 2 'apply_flag n a/b'      "-n with slash rejected"
true_   "apply_flag n valid" 'apply_flag n goodname'

## -H / -U set network off --------------------------------------------------
network=1; apply_flag H; eq "-H disables network" "$network" ""
network=1; untrusted=""; apply_flag U
eq "-U disables network" "$network" ""
eq "-U sets untrusted"   "$untrusted" "1"

## -U neutralizes every credential-forwarding flag (not just config mounts) --
ssh_agent=1; docker_sock=/x; docker_remote=/y; gpg_forward=1; gcloud_creds=1
envs=("GH_TOKEN=t" "DOCKER_HOST=unix://y" "MYVAR=keep"); warnings=()
apply_untrusted
eq "-U clears ssh_agent"   "$ssh_agent" ""
eq "-U clears docker_sock" "$docker_sock" ""
eq "-U clears gpg_forward" "$gpg_forward" ""
eq "-U clears gcloud"      "$gcloud_creds" ""
eq "-U drops cred envs, keeps the rest" "${envs[*]}" "MYVAR=keep"

## port_for -----------------------------------------------------------------
p1="$(port_for foo)"; p2="$(port_for foo)"; p3="$(port_for bar)"
eq "port deterministic" "$p1" "$p2"
true_ "port differs by name" '[ "$p1" != "$p3" ]'
true_ "port in widened range" '[ "$p1" -ge 10000 ] && [ "$p1" -le 59999 ]'

## mount matrix -------------------------------------------------------------
reset_mounts() { mount_tags=(); mount_srcs=(); mount_dests=(); mount_modes=(); }
mount_mode() { # echo the mode for dest $1, or empty if absent
    local i
    for i in "${!mount_dests[@]}"; do
        [ "${mount_dests[$i]}" = "$1" ] && { printf '%s' "${mount_modes[$i]}"; return; }
    done
}
run_assemble() { # $1 extra setup expr
    reset_mounts
    name=testbox; primary="$PROJ"; dirs=("$PROJ")
    no_copy=""; gcloud_creds=""; untrusted=""; extra_dirs=(); extra_modes=()
    eval "${1:-:}"
    assemble_mounts
}
slug_dest="/home/$USER/.claude/projects/${PROJ//\//-}"
LIB="$fixture/lib"; mkdir -p "$LIB"

run_assemble
eq "default: project rw"         "$(mount_mode "$PROJ")" "rw"
eq "default: .claude cfg ro"     "$(mount_mode /mnt/qemubox-cfg/.claude)" "ro"
eq "default: per-slug memory rw" "$(mount_mode "$slug_dest")" "rw"

run_assemble 'untrusted=1'
eq   "untrusted: project still rw"     "$(mount_mode "$PROJ")" "rw"
eq   "untrusted: no .claude cfg mount" "$(mount_mode /mnt/qemubox-cfg/.claude)" ""
eq   "untrusted: no qemubox-home"      "$(mount_mode /mnt/qemubox-home)" ""
eq   "untrusted: no per-slug memory"   "$(mount_mode "$slug_dest")" ""

run_assemble 'no_copy=1'
eq "no-project: project not mounted" "$(mount_mode "$PROJ")" ""

run_assemble 'extra_dirs=("'"$LIB"'"); extra_modes=(ro)'
eq "extra -v mount honors ro mode" "$(mount_mode "$LIB")" "ro"

## status_box ---------------------------------------------------------------
mkdir -p "$QEMUBOX_HOME/sbx"
sout="$(status_box sbx)"
true_ "status: process stopped" '[[ "$sout" == *process=stopped* ]]'
true_ "status: boot pending"    '[[ "$sout" == *boot=pending* ]]'
exits 1 'status_box nonexistent-xyz' "status errors on unknown box"

echo "qemubox/test.sh: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
