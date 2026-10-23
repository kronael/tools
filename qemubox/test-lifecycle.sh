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
    echo disk > "$ROOT/two/upper.raw"
    touch "$ROOT/one/root.sock.pid" "$ROOT/one/cfg.sock.pid" \
        "$ROOT/two/qbx0.sock.pid" "$ROOT/two/capture.sock.pid"
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
for key, action in (("ExecStartPost", "_ready"), ("ExecStop", "_stop"),
                    ("ExecStopPost", "_cleanup")):
    command = shlex.split(properties[key])
    assert subprocess.check_output(command, text=True) == f"{action}\nvm\n"
    assert command == ["/bin/bash", source, action, "vm"]
stopped = pathlib.Path(sys.argv[3])
assert not stopped.exists()
PY
    cleanup_box vm
    [ -f "$ROOT/vm/stopped" ]
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
    [ "$(cat "$systemd_log")" = $'systemctl --user kill --kill-who=main -s SIGTERM qemubox@vm.service\nsystemctl --user stop qemubox@vm.service' ]
}
regression "stop asks systemd; -f sends SIGTERM then uses the manager stop deadline" stop_unit_test

shutdown_test() {
    regression_setup
    mkdir -p "$ROOT/vm/config"
    printf 'cfg\t%s\t/run/qemubox/config\tro\n' "$ROOT/vm/config" \
        > "$ROOT/vm/config/mounts"
    systemctl() { return 0; }
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
        [ "$3" = kill ] || return 0
        kill "$MAINPID"
        wait "$MAINPID" || true
    }
    shutdown_box vm
    [ "$(cat "$fixture/shutdown-qmp")" = cont ]
    [ "$(cat "$fixture/shutdown-ssh")" = 'vm sudo kill -TERM 1' ]
    [ ! -e "$ROOT/vm/stopped" ]
}
regression "_stop resumes and powers off a live guest; returns at once after qemu" shutdown_test

shutdown_missing_share_test() {
    regression_setup
    mkdir -p "$ROOT/vm/config"
    printf 'qbx0\t%s\t/project\trw\ncfg\t%s\t/run/qemubox/config\tro\n' \
        "$PROJ" "$ROOT/vm/config" > "$ROOT/vm/config/mounts"
    sleep 30 &
    MAINPID=$!
    trap 'kill "$MAINPID" 2>/dev/null || true; wait "$MAINPID" 2>/dev/null || true' EXIT
    systemctl() {
        printf '%s\n' "$*" >> "$fixture/share-health"
        [ "${!#}" != qemubox-fs@vm-cfg.service ]
    }
    ssh_plain_box() { touch "$fixture/bad-shutdown-ssh"; }
    qmp_box() { touch "$fixture/bad-shutdown-qmp"; }
    shutdown_box vm
    [ "$(wc -l < "$fixture/share-health")" = 2 ]
    [ ! -e "$fixture/bad-shutdown-ssh" ]
    [ ! -e "$fixture/bad-shutdown-qmp" ]
}
regression "lost share skips guest shutdown so systemd can terminate QEMU" \
    shutdown_missing_share_test

check_test() {
    regression_setup
    run_state() { echo running; }
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
    run_state() { echo running; }
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
    run_state() { echo running; }
    name=vm; session_pid=""
    mkdir -p "$ROOT/vm"
    echo disk > "$ROOT/vm/upper.raw"
    : > "$systemd_log"
    (LINGER=1; leave_session) 2> "$fixture/leave.err"
    [ "$(cat "$ROOT/vm/idle")" = 1 ]
    [ ! -s "$systemd_log" ]
    grep -q 'stops after 1s with no session' "$fixture/leave.err"
    (LINGER=0; leave_session) 2> /dev/null
    [ "$(cat "$ROOT/vm/idle")" = 0 ]
    [ "$(cat "$systemd_log")" = 'systemctl --user stop --no-block qemubox@vm.service' ]
    [ "$(cat "$ROOT/vm/upper.raw")" = disk ]
}
regression "leaving stamps idle; QEMUBOX_LINGER=0 stops at once" leave_test

setup_test() {
    regression_setup
    mkdir -p "$ROOT/vm/config"
    wait_ready() { echo "$1" > "$fixture/setup-ready"; }
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
    [ "$(cat "$fixture/setup-ready")" = vm ]
    grep -qxF "systemd-run --user --collect --quiet --unit=qemubox-check@vm --on-active=60 --on-unit-active=60 --timer-property=AccuracySec=1s --timer-property=BindsTo=qemubox@vm.service -E QEMUBOX_HOME=$ROOT -E PATH=$PATH -E QEMUBOX_RESUME_FREE=2048 /bin/bash $SELF _check vm" "$systemd_log"
    [ "$(cat "$fixture/check-command")" = $'_check\nvm' ]
}
regression "_ready waits for the guest, stamps idle and arms the check" setup_test

linger_test() {
    command() { return 0; }
    find_virtiofsd() { echo "$fixture/readonly-virtiofsd"; }
    printf '#!/bin/sh\necho --readonly\n' > "$fixture/readonly-virtiofsd"
    chmod +x "$fixture/readonly-virtiofsd"
    loginctl() { echo no; }
    if (missing_deps) 2> "$fixture/linger.err"; then exit 1; fi
    grep -q "loginctl enable-linger $(id -un)" "$fixture/linger.err"
    loginctl() { echo yes; }
    (missing_deps)
}
regression "launch requires lingering and names the command" linger_test

virtiofsd_deps_test() {
    mkdir -p "$fixture/bin"
    printf '#!/bin/sh\necho --readonly\n' > "$fixture/bin/virtiofsd"
    chmod +x "$fixture/bin/virtiofsd"
    PATH="$fixture/bin:$PATH"
    [ "$(find_virtiofsd)" = "$fixture/bin/virtiofsd" ]
    command() {
        if [ "$1" = -v ] && [ "$2" = virtiofsd ]
        then
            printf '%s\n' "$fixture/bin/virtiofsd"
        fi
    }
    loginctl() { echo yes; }
    (missing_deps)
    printf '#!/bin/sh\necho legacy-help\n' > "$fixture/bin/virtiofsd"
    if (missing_deps) 2> "$fixture/readonly-error"
    then
        return 1
    fi
    grep -q 'needs --readonly support' "$fixture/readonly-error"
    find_virtiofsd() { return 1; }
    if (missing_deps) 2> "$fixture/missing-virtiofsd"
    then
        return 1
    fi
    grep -qx 'Missing: virtiofsd' "$fixture/missing-virtiofsd"
}
regression "PATH virtiofsd wins; missing and writable-only daemons refuse launch" \
    virtiofsd_deps_test

share_units_test() {
    regression_setup
    stage_capture() { :; }
    untrusted=1
    mkdir -p "$fixture/unit,share \$literal"
    assemble_mounts() {
        reset_mounts
        add_mount "$fixture/unit,share \$literal" /readonly ro
        add_mount "$PROJ" /writable rw
    }
    find_virtiofsd() { echo /fake/virtiofsd; }
    missing_deps() { :; }
    local calls=0
    systemd-run() {
        calls=$((calls + 1))
        printf '%s\0' "$@" > "$fixture/share-unit-$calls"
    }
    start_box shares
    unlock_box
    python3 - "$fixture" "$ROOT/shares" <<'PY'
import pathlib
import sys

fixture, box = map(pathlib.Path, sys.argv[1:])
units = [f"qemubox-fs@shares-{tag}.service"
         for tag in ("qbx0", "qbx1", "cfg", "root")]
for n, (tag, source, readonly) in enumerate([
    ("qbx0", fixture / "unit,share $literal", True),
    ("qbx1", fixture / "proj", False),
    ("cfg", box / "config", True),
    ("root", box.parent / "base/fixture/rootfs", True),
], 1):
    args = (fixture / f"share-unit-{n}").read_bytes().decode().split("\0")[:-1]
    assert f"--unit=qemubox-fs@shares-{tag}.service" in args
    assert "--service-type=exec" in args
    assert "--expand-environment=no" in args
    assert "PartOf=qemubox@shares.service" in args
    cleanup = f'ExecStopPost=:/usr/bin/rm -f "{box}/{tag}.sock"'
    assert f'{cleanup} "{box}/{tag}.sock.pid"' in args
    command = args[args.index("/fake/virtiofsd"):]
    expected = ["/fake/virtiofsd", f"--socket-path={box}/{tag}.sock",
                f"--shared-dir={source}", "--sandbox=none"]
    if readonly:
        expected.append("--readonly")
    if tag == "root":
        import os
        expected += ["--cache=always", "--translate-uid", f"map:0:{os.getuid()}:1",
                     "--translate-gid", f"map:0:{os.getgid()}:1"]
    assert command == expected, command
args = (fixture / "share-unit-5").read_bytes().decode().split("\0")[:-1]
for key in ("BindsTo", "After"):
    assert f"{key}={' '.join(units)}" in args
assert "QEMUBOX_READY_TIMEOUT=180" in args
assert "QEMUBOX_RESUME_FREE=2048" in args
PY
    : > "$systemd_log"
    cleanup_box shares
    [ "$(cat "$systemd_log")" = \
        'systemctl --user stop --no-block qemubox-fs@shares-qbx0.service qemubox-fs@shares-qbx1.service qemubox-fs@shares-cfg.service qemubox-fs@shares-root.service' ]
    [ -f "$ROOT/shares/stopped" ]
}
regression "share units enforce readonly, include cfg, order QEMU and stop at teardown" \
    share_units_test

share_failure_test() {
    regression_setup
    stage_capture() { :; }
    untrusted=1
    assemble_mounts() {
        reset_mounts
        add_mount "$PROJ" /first rw
        add_mount "$PROJ" /second ro
    }
    missing_deps() { :; }
    find_virtiofsd() { echo /fake/virtiofsd; }
    local failed=qemubox-fs@shares-qbx1.service
    systemd-run() {
        printf '%s\n' "$*" >> "$fixture/share-failure-units"
        [[ " $* " != *" --unit=$failed "* ]]
    }
    : > "$systemd_log"
    if start_box shares
    then
        return 1
    fi
    unlock_box
    grep -Fxq \
        'systemctl --user stop qemubox-fs@shares-qbx0.service qemubox-fs@shares-qbx1.service' \
        "$systemd_log"
    ! grep -q 'shares-cfg' "$systemd_log"
    ! grep -q -- '--unit=qemubox@shares.service' "$fixture/share-failure-units"
    failed=qemubox@shares.service
    : > "$systemd_log"
    if start_box shares
    then
        return 1
    fi
    unlock_box
    grep -Fxq \
        'systemctl --user stop qemubox-fs@shares-qbx0.service qemubox-fs@shares-qbx1.service qemubox-fs@shares-cfg.service qemubox-fs@shares-root.service' \
        "$systemd_log"
    grep -q 'journalctl --user -u qemubox@shares.service' "$systemd_log"
}
regression "daemon startup failure and VM startup failure stop every started share" \
    share_failure_test

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
    echo disk > "$ROOT/vm/upper.raw"
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
    run_state() { echo paused:prelaunch; }
    if wait_ready vm 2> "$fixture/paused"; then exit 1; fi
    grep -q 'is paused:prelaunch' "$fixture/paused"
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
