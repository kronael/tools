#!/usr/bin/env bash
set -uo pipefail

here="$(cd "$(dirname "$0")" && pwd)"
fixture="$(mktemp -d)"
trap 'rm -rf "$fixture"' EXIT

export HOME="$fixture/home"
export QEMUBOX_HOME="$fixture/state"
mkdir -p "$HOME/.claude" "$HOME/.codex" "$HOME/.agents" "$QEMUBOX_HOME"
PROJ="$fixture/proj"; mkdir -p "$PROJ"

# shellcheck disable=SC1090
QEMUBOX_LIB=1 . "$here/qemubox"
set +e

systemd_log="$fixture/systemd.log"
systemctl() {
    printf 'systemctl %s\n' "$*" >> "$systemd_log"
    case "$2" in
        is-active) echo inactive; return 3 ;;
        show) echo "${memory_current:-[not set]}" ;;
    esac
}
systemd-run() {
    printf 'systemd-run %s\n' "$*" >> "$systemd_log"
    local arg
    for arg in "$@"
    do
        case "$arg" in
            --socket-path=*)
                python3 - "${arg#*=}" <<'PY'
import socket
import sys
with socket.socket(socket.AF_UNIX) as sock:
    sock.bind(sys.argv[1])
PY
                ;;
        esac
    done
}
journalctl() { printf 'journalctl %s\n' "$*" >> "$systemd_log"; }
loginctl() { echo yes; }
ss() { :; }
fake_qemu="$fixture/fake-qemu"
printf '#!/bin/sh\nprintf "%%s\\n" "$@" > "$QEMU_ARGS"\n' > "$fake_qemu"
chmod +x "$fake_qemu"

pass=0; fail=0
ok()   { pass=$((pass+1)); }
bad()  { fail=$((fail+1)); echo "FAIL: $1" >&2; }
eq()   { [ "$2" = "$3" ] && ok || bad "$1: expected '$3' got '$2'"; }
true_() { if eval "$2"; then ok; else bad "$1"; fi; }
false_(){ if eval "$2"; then bad "$1"; else ok; fi; }

exits() { ( eval "$2" ) >/dev/null 2>&1; [ "$?" = "$1" ] && ok || bad "$3"; }

regression() {
    (set -e; "$2") > "$fixture/regression.log" 2>&1
    if [ "$?" = 0 ]; then ok; else cat "$fixture/regression.log"; bad "$1"; fi
}


regression_setup() {
    ROOT="$fixture/refine-$BASHPID"
    mkdir -p "$ROOT/base"
    echo fixture > "$ROOT/base/current"
    for suffix in qcow2 vmlinuz initrd; do echo base > "$ROOT/base/fixture.$suffix"; done
    dirs=()
    qemu-img() { touch "$dir/disk.qcow2"; }
    bsdtar() { :; }
    mke2fs() { :; }
}

eq "box_name plain" "$(box_name repo)" "repo"
eq "box_name slash->dash" "$(box_name a/b)" "a-b"
eq "box_name default" "$(box_name)" "default"

false_ "rm empty pattern matches nothing"    'rm_matches anything ""'
true_  "rm '\''*'\'' matches all"                 'rm_matches anything "*"'
true_  "rm exact match"                      'rm_matches web-api web-api'
false_ "rm exact does not substring-match"   'rm_matches web-api-facade web-api'
true_  "rm glob star"                        'rm_matches repo-1 "repo-*"'
false_ "rm glob non-match"                   'rm_matches other "repo-*"'

eq "copy_arg abs"        "$(copy_arg /a/b)" "/a/b"
eq "copy_arg strip :rw"  "$(copy_arg /a/b:rw)" "/a/b"
eq "copy_arg strip :ro"  "$(copy_arg /a/b:ro)" "/a/b"
eq "copy_arg keep inner colon" "$(copy_arg /a:b:rw)" "/a:b"
exits 2 'copy_arg rel' "copy_arg rejects relative path"

exits 2 'apply_flag n ..'       "-n .. rejected"
exits 2 'apply_flag n .'        "-n . rejected"
exits 2 'apply_flag n base'     "-n base rejected"
exits 2 'apply_flag n .locks'   "-n .locks rejected"
exits 2 'apply_flag n ""'       "-n empty rejected"
exits 2 'apply_flag n a/b'      "-n with slash rejected"
true_   "apply_flag n valid" 'apply_flag n goodname'

network=1; apply_flag H; eq "-H disables network" "$network" ""
network=1; untrusted=""; apply_flag U
eq "-U disables network" "$network" ""
eq "-U sets untrusted"   "$untrusted" "1"

ssh_agent=1; docker_sock=/x; docker_remote=/y; gpg_forward=1; gcloud_creds=1
envs=("GH_TOKEN=t" "DOCKER_HOST=unix://y" "MYVAR=keep" "CLAUDE_CODE_OAUTH_TOKEN=o"
    "OPENAI_API_KEY=a" "CODEX_API_KEY=c"); warnings=()
apply_untrusted
eq "-U clears ssh_agent"   "$ssh_agent" ""
eq "-U clears docker_sock" "$docker_sock" ""
eq "-U clears gpg_forward" "$gpg_forward" ""
eq "-U clears gcloud"      "$gcloud_creds" ""
eq "-U drops cred envs and agent tokens, keeps the rest" "${envs[*]}" "MYVAR=keep"
for tool in codex opus; do
    cmd=(); tool_cmd "$tool"; warnings=(); apply_untrusted
    true_ "-U warns that $tool cannot authenticate" \
        'printf "%s\n" "${warnings[@]}" | grep -q "cannot authenticate"'
done
cmd=(); tool_cmd bash; warnings=(); apply_untrusted
false_ "-U does not warn for a shell" \
    'printf "%s\n" "${warnings[@]}" | grep -q "cannot authenticate"'
cmd=()

p1="$(port_for foo)"; p2="$(port_for foo)"; p3="$(port_for bar)"
eq "port deterministic" "$p1" "$p2"
true_ "port differs by name" '[ "$p1" != "$p3" ]'
true_ "port in widened range" '[ "$p1" -ge 10000 ] && [ "$p1" -le 59999 ]'
mkdir -p "$QEMUBOX_HOME/pbx"; echo 54321 > "$QEMUBOX_HOME/pbx/port"
eq "port_for reads persisted \$dir/port" "$(port_for pbx)" "54321"

source "$here/test-mounts.sh"

run_assemble
persist_builds=""; eph_no_tmpfs=""; stage_ephemeral "$eph"
network=1; gout="$(guest_note myhost "$eph")"
true_ "note names the sandbox"     '[[ "$gout" == *CLAUDE_SANDBOX=qemubox* ]]'
true_ "note names the host"        '[[ "$gout" == *"host \`myhost\`"* ]]'
true_ "note: network on"           '[[ "$gout" == *"Outbound network: on."* ]]'
true_ "note marks the project rw"  '[[ "$gout" == *"- $PROJ (rw) <- same path"* ]]'
true_ "note maps config to host"   '[[ "$gout" == *"- $HOME/.claude (rw) <- same path"* ]]'
true_ "note lists shared history" '[[ "$gout" == *"- $HOME/.claude (rw) <- same path"* ]]'
true_ "note lists the empty dependency dirs" \
    '[[ "$gout" == *"empty box-only mounts."*"  - $PROJ/server/.venv"* ]]'
false_ "note omits a dependency dir absent at launch" '[[ "$gout" == *"$PROJ/.turbo"* ]]'
network=""; gout="$(guest_note myhost "$eph")"
true_ "note: network off"          '[[ "$gout" == *"Outbound network: off."* ]]'
false_ "note names no tmpfs workdir without -T" '[[ "$gout" == *"working dir"* ]]'
for flag in P B; do
    run_assemble
    persist_builds=""; eph_no_tmpfs=""; apply_flag "$flag"
    stage_ephemeral "$eph"; gout="$(guest_note myhost "$eph")"
    false_ "-$flag note claims no empty dependency dir" '[[ "$gout" == *box-only* ]]'
done
persist_builds=""; eph_no_tmpfs=""
dirs=(); apply_flag T
stage_ephemeral "$eph"; gout="$(guest_note myhost "$eph")"
false_ "-T note claims no empty dependency dir" '[[ "$gout" == *box-only* ]]'
true_ "-T note names the tmpfs workdir" \
    '[[ "$gout" == *"working dir /tmp/work is guest tmpfs"* ]]'
tmp_session=""

mkdir -p "$QEMUBOX_HOME/sbx"
sout="$(status_box sbx)"
true_ "status: unit inactive" '[[ "$sout" == *unit=inactive* ]]'
true_ "status: state stopped" '[[ "$sout" == *state=stopped* ]]'
exits 1 'status_box nonexistent-xyz' "status errors on unknown box"

eq "default RAM" "$MEM" "24576"
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
    missing_deps() { :; }
    dirs=("$PROJ"); name=identitybox; network=""; untrusted=""
    : > "$systemd_log"
    start_box identitybox
    if flock -n "$ROOT/.locks/identitybox" true; then exit 1; fi
    unlock_box
    grep -qF -- "-E QEMUBOX_HOME=$ROOT -E QEMUBOX_MEM=24576 -E QEMUBOX_CPUS=4 -E QEMUBOX_QEMU=qemu-system-x86_64 " "$systemd_log"
    grep -q -- '-p TimeoutStartSec=180 -p TimeoutStopSec=100' "$systemd_log"
    grep -qFx "$PROJ"$'\t'"$PROJ"$'\t'rw \
        < <(cut -f2- "$ROOT/identitybox/config/mounts")
    [ "$(tail -1 "$ROOT/identitybox/config/mounts")" = \
        cfg$'\t'"$ROOT/identitybox/config"$'\t'/run/qemubox/config$'\t'ro ]
    [ "$(cat "$ROOT/identitybox/net")" = off ]
    grep -q 'CLAUDE_SANDBOX=qemubox' "$ROOT/identitybox/config/CLAUDE.md"
    echo retained > "$ROOT/identitybox/disk.qcow2"
    ensure_box identitybox
    [ "$(cat "$ROOT/identitybox/disk.qcow2")" = retained ]
    (QEMU="$fake_qemu" QEMU_ARGS="$fixture/qemu.args" run_qemu identitybox)
    grep -Fx -- '-kernel' "$fixture/qemu.args"
    grep -Fx -- '-initrd' "$fixture/qemu.args"
    grep -Fx -- 'root=/dev/vda rw console=ttyS0 noresume loglevel=5' "$fixture/qemu.args"
    grep -Fx -- 'virtio-balloon-pci,free-page-reporting=on' "$fixture/qemu.args"
    grep -Fx -- 'socket,id=cfg,path=cfg.sock' "$fixture/qemu.args"
    grep -Fx -- 'vhost-user-fs-pci,queue-size=1024,chardev=cfg,tag=cfg' \
        "$fixture/qemu.args"
    grep -Fx -- 'memory-backend-memfd,id=mem,size=24576M,share=on' \
        "$fixture/qemu.args"
    grep -Fx -- node,memdev=mem "$fixture/qemu.args"
    [ "$(grep -Fxc -- -chardev "$fixture/qemu.args")" = \
        "$(wc -l < "$ROOT/identitybox/config/mounts")" ]
    grep -Fx -- "user,model=virtio,restrict=on,hostfwd=tcp:127.0.0.1:$(cat "$ROOT/identitybox/port")-:22" "$fixture/qemu.args"
    [ "$(grep -A1 -Fx -- -serial "$fixture/qemu.args" | tail -1)" = stdio ]
    if grep -qE -- '^-(virtfs|daemonize|pidfile)$|seed.iso' "$fixture/qemu.args"; then exit 1; fi
    : > "$systemd_log"
    systemctl() { printf 'systemctl %s\n' "$*" >> "$systemd_log"; echo active; }
    qmp_box() { echo running; }
    rm "$ROOT/identitybox/net"
    start_box identitybox
    unlock_box
    [ ! -e "$ROOT/identitybox/net" ]
    if grep -q systemd-run "$systemd_log"; then exit 1; fi
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
bsdtar() { :; }
mke2fs() { :; }
qemu-img() { :; }
exits 42 'build_base' "export failure stays visible"
eq "failed export container removed" "$(cat "$fixture/removed-container")" "fixture-container"
false_ "failed export temp dir removed" '[ -d "$(dirname "$(cat "$fixture/export-path")")" ]'
unset QEMUBOX_DOCKER
unset -f bsdtar mke2fs qemu-img

source "$here/test-lifecycle.sh"
source "$here/test-parity.sh"
source "$here/test-cli.sh"

source "$here/test-refine.sh"
source "$here/test-image.sh"
source "$here/test-boot.sh"

echo "qemubox/test.sh: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
