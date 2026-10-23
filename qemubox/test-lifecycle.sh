true_ "rm accepts ls prefix" 'rm_matches repo qemubox-repo'
true_ "rm accepts prefixed glob" 'rm_matches repo-1 "qemubox-repo-*"'
exits 2 'remove_boxes' "rm requires names"
exits 1 'remove_boxes nonexistent-xyz' "rm fails on no match"
exits 2 'remove_boxes --bad' "rm rejects unknown options"

(
    set -e
    ROOT="$fixture/removal"
    mkdir -p "$ROOT/one" "$ROOT/two" "$ROOT/keep"
    echo disk > "$ROOT/one/disk.qcow2"
    echo disk > "$ROOT/two/disk.qcow2"
    remove_boxes qemubox-one 'tw*'
    [ ! -d "$ROOT/one" ]
    [ ! -d "$ROOT/two" ]
    [ -d "$ROOT/keep" ]
    touch "$ROOT/keep/unknown"
    if remove_boxes keep; then exit 1; fi
) > "$fixture/removal.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/removal.log"; bad "rm multiple targets and failures"; }

exits 2 'stop_boxes' "stop requires names"
exits 2 'stop_boxes -f' "stop -f alone requires names"
exits 2 'stop_boxes --bad one' "stop rejects unknown options"
(
    set -e
    ROOT="$fixture/stopping"
    mkdir -p "$ROOT/one" "$ROOT/two" "$ROOT/down"
    run_state() { if [ "$1" = down ]; then echo stopped; else echo running; fi; }
    stop_box() { echo "$1 ${2:-graceful}" >> "$fixture/stop-args"; }
    stop_boxes qemubox-one
    stop_boxes two -f
    stop_boxes -f 'o*' down 2> "$fixture/stop-skipped"
    [ "$(cat "$fixture/stop-args")" = $'one graceful\ntwo force\none force' ]
    grep -q 'qemubox-down is not running' "$fixture/stop-skipped"
    if stop_boxes nonexistent-xyz; then exit 1; fi
    [ "$(cat "$fixture/stop-args")" = $'one graceful\ntwo force\none force' ]
    stop_boxes -a 2> "$fixture/stop-skipped"
    [ "$(cat "$fixture/stop-args")" = $'one graceful\ntwo force\none force\none graceful\ntwo graceful' ]
    grep -q 'qemubox-down is not running' "$fixture/stop-skipped"
) > "$fixture/stop.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/stop.log"; bad "stop: -f anywhere, -a, rm matching, stopped boxes skipped"; }

run_state_test() {
    unit=failed
    systemctl() { echo "$unit"; }
    qmp_box() { echo io-error; }
    [ "$(run_state vm)" = stopped ]
    unit=active
    [ "$(run_state vm)" = paused:io-error ]
    unit=activating
    qmp_box() { return 1; }
    [ "$(run_state vm)" = "?" ]
}
regression "state: inactive or failed unit is stopped, else QMP decides" run_state_test

service_commands_test() {
    regression_setup
    mv "$ROOT" "$ROOT with spaces"
    ROOT="$ROOT with spaces"
    SELF="$fixture/source directory/qemubox"
    mkdir -p "${SELF%/*}"
    printf '#!/bin/sh\nprintf "%%s\\n" "$@"\n' > "$SELF"
    chmod 644 "$SELF"
    untrusted=""
    missing_deps() { :; }
    assemble_mounts() { mount_tags=(); mount_srcs=(); mount_dests=(); mount_modes=(); }
    systemd-run() { printf '%s\0' "$@" > "$fixture/service-args"; }
    start_box vm
    unlock_box
    python3 - "$fixture/service-args" "$SELF" "$ROOT/vm/stopped" <<'PY'
import pathlib
import shlex
import subprocess
import sys

args = pathlib.Path(sys.argv[1]).read_bytes().decode().split("\0")[:-1]
properties = {}
index = 0
while args[index].startswith("-"):
    if args[index] in ("-p", "-E"):
        if args[index] == "-p":
            key, value = args[index + 1].split("=", 1)
            properties[key] = value
        index += 1
    index += 1
source = sys.argv[2]
command = args[index:]
assert subprocess.check_output(command, text=True) == "_vm\nvm\n"
assert command == ["/bin/bash", source, "_vm", "vm"]
for key, action in (("ExecStartPost", "_ready"), ("ExecStop", "_stop")):
    command = shlex.split(properties[key])
    assert subprocess.check_output(command, text=True) == f"{action}\nvm\n"
    assert command == ["/bin/bash", source, action, "vm"]
stopped = pathlib.Path(sys.argv[3])
assert not stopped.exists()
command = shlex.split(properties["ExecStopPost"])
assert command == ["/usr/bin/touch", str(stopped)]
subprocess.run(command, check=True)
assert stopped.is_file()
PY
}
regression "unit commands run a non-executable source with spaces and stamp stop completion" \
    service_commands_test

stop_unit_test() {
    : > "$systemd_log"
    stop_box vm
    [ "$(cat "$systemd_log")" = 'systemctl --user stop qemubox@vm.service' ]
    : > "$systemd_log"
    run_state() { echo running; }
    sleep() { echo 'Stop must use the systemd deadline' >&2; return 1; }
    stop_box vm force
    [ "$(cat "$systemd_log")" = $'systemctl --user kill -s SIGTERM qemubox@vm.service\nsystemctl --user stop qemubox@vm.service' ]
}
regression "stop asks systemd; -f sends SIGTERM then uses the manager stop deadline" stop_unit_test

shutdown_test() {
    regression_setup
    mkdir -p "$ROOT/vm"
    ssh_plain_box() { echo "$*" >> "$fixture/shutdown-ssh"; }
    qmp_box() { echo "$2" >> "$fixture/shutdown-qmp"; }
    unset MAINPID
    shutdown_box vm
    [ ! -e "$ROOT/vm/stopped" ]
    [ ! -e "$fixture/shutdown-ssh" ]
    [ ! -e "$fixture/shutdown-qmp" ]
    sleep 30 &
    MAINPID=$!
    ssh_plain_box() {
        [ ! -e "$ROOT/vm/stopped" ]
        echo "$*" >> "$fixture/shutdown-ssh"
        [ "$3" = poweroff ] || return 0
        kill "$MAINPID"
        wait "$MAINPID" || true
    }
    shutdown_box vm
    [ "$(cat "$fixture/shutdown-qmp")" = cont ]
    [ "$(cat "$fixture/shutdown-ssh")" = $'vm sudo fstrim /\nvm sudo poweroff' ]
    [ ! -e "$ROOT/vm/stopped" ]
}
regression "_stop resumes and powers off a live guest; returns at once after qemu" shutdown_test

check_test() {
    regression_setup
    mkdir -p "$ROOT/vm"
    : > "$systemd_log"
    check_box vm
    echo 60 > "$ROOT/vm/idle"
    check_box vm
    touch -d '2 minutes ago' "$ROOT/vm/idle"
    session_count() { echo 1; }
    check_box vm
    [ ! -s "$systemd_log" ]
    session_count() { echo 0; }
    check_box vm 2> "$fixture/check.err"
    [ "$(cat "$systemd_log")" = 'systemctl --user stop --no-block qemubox@vm.service' ]
    grep -q 'no session for 60s' "$fixture/check.err"
}
regression "_check stops only a box idle past its linger with no session" check_test

check_count_failure_test() {
    regression_setup
    mkdir -p "$ROOT/vm"
    echo 0 > "$ROOT/vm/idle"
    ss() { echo 'Session probe failed' >&2; return 17; }
    : > "$systemd_log"
    if check_box vm 2> "$fixture/count-error"
    then
        return 1
    else
        [ "$?" -eq 17 ]
    fi
    [ ! -s "$systemd_log" ]
    grep -qx 'Session probe failed' "$fixture/count-error"
}
regression "failed session lookup preserves its error and never stops the VM" \
    check_count_failure_test

list_count_failure_test() {
    regression_setup
    mkdir -p "$ROOT/vm"
    run_state() { echo running; }
    ssh_plain_box() { return 1; }
    ss() { return 17; }
    [[ "$(list_boxes)" = *$'running\t?\t'* ]]
}
regression "failed session lookup displays unknown use in the VM list" \
    list_count_failure_test

session_count_test() {
    regression_setup
    mkdir -p "$ROOT/vm"
    echo 43210 > "$ROOT/vm/port"
    ss() { echo "$*" > "$fixture/ss-args"; printf 'a\nb\n'; }
    [ "$(session_count vm)" = 2 ]
    [ "$(cat "$fixture/ss-args")" = '-Htn state established ( dport = :43210 )' ]
}
regression "sessions are established connections to the box port" session_count_test

leave_test() {
    regression_setup
    name=vm; session_pid=""
    mkdir -p "$ROOT/vm"
    echo disk > "$ROOT/vm/disk.qcow2"
    : > "$systemd_log"
    (LINGER=1; leave_session) 2> "$fixture/leave.err"
    [ "$(cat "$ROOT/vm/idle")" = 1 ]
    [ ! -s "$systemd_log" ]
    grep -q 'stops after 1s with no session' "$fixture/leave.err"
    (LINGER=0; leave_session) 2> /dev/null
    [ "$(cat "$ROOT/vm/idle")" = 0 ]
    [ "$(cat "$systemd_log")" = 'systemctl --user stop --no-block qemubox@vm.service' ]
    [ "$(cat "$ROOT/vm/disk.qcow2")" = disk ]
}
regression "leaving stamps idle; QEMUBOX_LINGER=0 stops at once" leave_test

setup_test() {
    regression_setup
    mkdir -p "$ROOT/vm/config"
    printf 'qbx0\t/src dir\t/dest dir\tro\n' > "$ROOT/vm/config/mounts"
    echo untrusted > "$ROOT/vm/trust"
    wait_ready() { :; }
    setup_guest_tmp() { :; }
    setup_guest_builds() { :; }
    setup_guest_runtime() { :; }
    setup_guest_limits() { :; }
    sync_guest_clock() { :; }
    mount_host_paths() { printf '%s|' "${mount_srcs[@]}" "${mount_modes[@]}" > "$fixture/setup-mounts"; }
    setup_guest_sessions() { echo "$untrusted" > "$fixture/setup-trust"; }
    SELF="$fixture/check source/qemubox"
    mkdir -p "${SELF%/*}"
    printf '#!/bin/sh\nprintf "%%s\\n" "$@"\n' > "$SELF"
    chmod 644 "$SELF"
    systemd-run() {
        printf 'systemd-run %s\n' "$*" >> "$systemd_log"
        while [[ "$1" = -* ]]
        do
            [ "$1" != -E ] || shift
            shift
        done
        "$@" > "$fixture/check-command"
    }
    LINGER=77
    : > "$systemd_log"
    setup_box vm
    [ "$(cat "$ROOT/vm/idle")" = 77 ]
    [ "$(cat "$fixture/setup-mounts")" = '/src dir|ro|' ]
    [ "$(cat "$fixture/setup-trust")" = 1 ]
    grep -qxF "systemd-run --user --collect --quiet --unit=qemubox-check@vm --on-active=60 --on-unit-active=60 --timer-property=BindsTo=qemubox@vm.service -E QEMUBOX_HOME=$ROOT -E PATH=$PATH /bin/bash $SELF _check vm" "$systemd_log"
    [ "$(cat "$fixture/check-command")" = $'_check\nvm' ]
}
regression "_ready sets up the guest from box files, stamps idle, arms the check" setup_test

linger_test() {
    command() { return 0; }
    loginctl() { echo no; }
    if (missing_deps) 2> "$fixture/linger.err"; then exit 1; fi
    grep -q "loginctl enable-linger $(id -un)" "$fixture/linger.err"
    loginctl() { echo yes; }
    (missing_deps)
}
regression "launch requires lingering and names the command" linger_test

(
    set -e
    ROOT="$fixture/pruning"
    mkdir -p "$ROOT"/{old,young,busy,stopped,booting}
    for n in old young busy stopped; do echo 1200 > "$ROOT/$n/idle"; done
    touch -d '5 hours ago' "$ROOT"/{old,busy,stopped}/idle
    run_state() { if [ "$1" = stopped ]; then echo stopped; else echo running; fi; }
    session_count() { if [ "$1" = busy ]; then echo 1; else echo 0; fi; }
    : > "$systemd_log"
    prune_boxes 2> /dev/null
    [ "$(cat "$systemd_log")" = 'systemctl --user stop --no-block qemubox@old.service' ]
    [ -d "$ROOT/stopped" ]
) > "$fixture/prune.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/prune.log"; bad "prune stops only boxes idle 4h with no session; removes no VM"; }

(
    set -e
    ROOT="$fixture/rm-stopped"
    mkdir -p "$ROOT"/{old,recent,up,base}
    touch "$ROOT/old/stopped" "$ROOT/recent/stopped"
    touch -d '3 hours ago' "$ROOT/old/stopped"
    run_state() { if [ "$1" = up ]; then echo running; else echo stopped; fi; }
    remove_box() { echo "$1" >> "$fixture/rm-stopped.removed"; }
    [ "$(remove_boxes --stopped 2)" = qemubox-old ]
    [ "$(cat "$fixture/rm-stopped.removed")" = old ]
) > "$fixture/rm-stopped.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/rm-stopped.log"; bad "rm --stopped removes only VMs stopped over the age"; }
(
    set -e
    ROOT="$fixture/rm-stopped-race"
    mkdir -p "$ROOT"/{old,restarted,flipped,base}
    touch -d '3 hours ago' "$ROOT"/{old,restarted,flipped}/stopped
    up=""
    run_state() { if [ "$1" = "$up" ]; then echo running; else echo stopped; fi; }
    lock_box() {
        case "$1" in
            restarted) touch "$ROOT/restarted/stopped" ;;
            flipped) up=flipped ;;
        esac
    }
    unlock_box() { :; }
    remove_box() { echo "$1" >> "$fixture/rm-stopped-race.removed"; }
    remove_boxes --stopped 2 > /dev/null 2>&1
    [ "$(cat "$fixture/rm-stopped-race.removed")" = old ]
) > "$fixture/rm-stopped-race.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/rm-stopped-race.log"; bad "rm --stopped rechecks running and age under the lock"; }
exits 2 'remove_boxes --stopped' "rm --stopped requires hours"
exits 2 'remove_boxes --stopped bad' "rm --stopped rejects invalid hours"
exits 2 'remove_boxes --stopped 2 one' "rm --stopped takes no names"

(
    set -e
    ROOT="$fixture/listing"
    mkdir -p "$ROOT/vm"
    echo disk > "$ROOT/vm/disk.qcow2"
    run_state() { echo running; }
    session_count() { echo 1; }
    memory_current=10485760
    ssh_plain_box() { printf '%s\n' 'x[$(touch "$fixture/pwned")0]' 1 1 1; }
    list_boxes > /dev/null
    [ ! -e "$fixture/pwned" ]
    ssh_plain_box() { printf '%s\n' 100 40 30 10; }
    [[ "$(list_boxes)" = *$'running\tbusy\t10M\t60K\t20K\t10K\t'* ]]
    grep -qx 'systemctl --user show -p MemoryCurrent --value qemubox@vm.service' "$systemd_log"
    unset -f ssh_plain_box
    output=$(list_boxes)
    [[ "$output" = NAME$'\t'STATUS$'\t'USE$'\t'RAM$'\t'USED$'\t'CACHE$'\t'TMPFS$'\t'DISK$'\t'PATH* ]]
    session_count() { echo 0; }
    memory_current='[not set]'
    [[ "$(list_boxes)" = *$'running\tidle\t?\t'* ]]
) > "$fixture/list.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/list.log"; bad "ls columns from systemd and the session count"; }

(
    set -e
    ROOT="$fixture/readiness"
    mkdir -p "$ROOT/vm"
    sleep() { :; }
    ssh_plain_box() { [ -e "$fixture/guest-ready" ] || { touch "$fixture/guest-ready"; return 255; }; }
    run_state() { echo running; }
    wait_ready vm
    [ -e "$fixture/guest-ready" ]
    rm "$fixture/guest-ready"
    run_state() { echo paused:io-error; }
    if wait_ready vm 2> "$fixture/paused"; then exit 1; fi
    grep -q 'is paused:io-error' "$fixture/paused"
    : > "$systemd_log"
    ready_error vm 2> /dev/null
    grep -qx 'journalctl --user -u qemubox@vm.service -n 40 --no-pager' "$systemd_log"
    lock_box vm
    (
        lock_box vm
        echo acquired > "$fixture/acquired"
        unlock_box
    ) &
    waiter=$!
    command sleep 0.1
    [ ! -f "$fixture/acquired" ]
    if (QEMUBOX_READY_TIMEOUT=0.1; lock_box vm) 2> "$fixture/lock.err"; then exit 1; fi
    grep -q 'stayed locked by another launch or rm' "$fixture/lock.err"
    unlock_box
    wait "$waiter"
    [ -f "$fixture/acquired" ]
) > "$fixture/ready.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/ready.log"; bad "ready wait, paused refusal, journal tail and lock wait"; }
