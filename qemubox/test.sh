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
false_ "rm empty pattern matches nothing"    'rm_matches anything ""'
true_  "rm '\''*'\'' matches all"                 'rm_matches anything "*"'
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
mkdir -p "$QEMUBOX_HOME/pbx"; echo 54321 > "$QEMUBOX_HOME/pbx/port"
eq "port_for reads persisted \$dir/port" "$(port_for pbx)" "54321"

source "$here/test-mounts.sh"

## status_box ---------------------------------------------------------------
mkdir -p "$QEMUBOX_HOME/sbx"
sout="$(status_box sbx)"
true_ "status: process stopped" '[[ "$sout" == *process=stopped* ]]'
true_ "status: boot pending"    '[[ "$sout" == *boot=pending* ]]'
exits 1 'status_box nonexistent-xyz' "status errors on unknown box"

eq "default RAM" "$MEM" "16384"
eq "default CPUs" "$CPUS" "4"
eq "default disk" "$DISK" "40G"
eq "guest user matches host" "$GUEST_USER" "$(id -un)"
eq "guest home matches passwd" "$GUEST_HOME" "$(getent passwd "$(id -u)" | cut -d: -f6)"

(
    set -e
    mkdir -p "$ROOT/base"
    printf '%s\n' fixture > "$ROOT/base/current"
    for suffix in qcow2 vmlinuz initrd; do echo base > "$ROOT/base/fixture.$suffix"; done
    qemu-img() { printf '%s\n' "$@" > "$fixture/qemu-img.args"; touch "$dir/disk.qcow2"; }
    ensure_box identitybox
    head -4 "$ROOT/identitybox/config/identity" > "$fixture/actual-identity"
    printf '%s\n' "$(id -un)" "$(id -u)" "$(id -g)" "$GUEST_HOME" > "$fixture/want-identity"
    cmp "$fixture/actual-identity" "$fixture/want-identity"
    cmp "$ROOT/identitybox/key.pub" "$ROOT/identitybox/config/authorized_keys"
    [ "$(cat "$ROOT/identitybox/image-id")" = fixture ]
    [ "$(tail -1 "$fixture/qemu-img.args")" = 40G ]
    QEMU=fake_qemu
    fake_qemu() { printf '%s\n' "$@" > "$fixture/qemu.args"; }
    missing_deps() { :; }
    ssh_plain_box() { :; }
    assemble_mounts() { :; }
    setup_guest_tmp() { :; }
    mount_host_paths() { :; }
    setup_guest_builds() { :; }
    setup_guest_runtime() { ! flock -n "$ROOT/.locks/identitybox" true; }
    setup_guest_auth() { :; }
    start_box identitybox
    [ -f "$ROOT/identitybox/ready" ]
    ! flock -n "$ROOT/.locks/identitybox" true
    unlock_box
    echo retained > "$ROOT/identitybox/disk.qcow2"
    ensure_box identitybox
    [ "$(cat "$ROOT/identitybox/disk.qcow2")" = retained ]
    grep -Fx -- '-kernel' "$fixture/qemu.args"
    grep -Fx -- '-initrd' "$fixture/qemu.args"
    grep -Fx -- 'root=/dev/vda rw console=ttyS0 noresume' "$fixture/qemu.args"
    grep -F -- 'mount_tag=qbxcfg,security_model=none,readonly=on' "$fixture/qemu.args"
    ! grep -q 'seed.iso' "$fixture/qemu.args"
) >"$fixture/boot-test.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/boot-test.log"; bad "identity and boot"; }
rm -f "$ROOT/base/fixture.vmlinuz"
exits 1 'ensure_box identitybox' "missing recorded base refuses VM"

fake_docker() {
    case "$1" in
        build) return 0 ;;
        image) printf 'sha256:%064d\n' 0 ;;
        create) echo fixture-container ;;
        export)
            echo "$3" > "$fixture/export-path"
            echo partial > "$3"
            return 42 ;;
        rm) echo "$2" > "$fixture/removed-container" ;;
    esac
}
QEMUBOX_DOCKER=fake_docker
exits 42 'build_base' "export failure stays visible"
eq "failed export container removed" "$(cat "$fixture/removed-container")" "fixture-container"
false_ "failed export temp dir removed" '[ -d "$(dirname "$(cat "$fixture/export-path")")" ]'
unset QEMUBOX_DOCKER

source "$here/test-lifecycle.sh"

echo "qemubox/test.sh: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
