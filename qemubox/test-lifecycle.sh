true_ "rm accepts ls prefix" 'rm_matches repo qemubox-repo'
true_ "rm accepts prefixed glob" 'rm_matches repo-1 "qemubox-repo-*"'
exits 2 'prune_boxes bad' "prune rejects invalid age"
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
    [ ! -d "$ROOT/one" ] && [ ! -d "$ROOT/two" ]
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
    running() { [ "$1" != down ]; }
    lock_box() { locked=1; }
    unlock_box() { locked=""; }
    stop_box() { echo "$1 ${2:-graceful}" >> "$fixture/stop-args"; }
    stop_boxes qemubox-one
    stop_boxes two -f
    stop_boxes -f 'o*' down 2> "$fixture/stop-skipped"
    [ "$(cat "$fixture/stop-args")" = $'one graceful\ntwo force\none force' ]
    grep -q 'qemubox-down is not running' "$fixture/stop-skipped"
    if stop_boxes nonexistent-xyz; then exit 1; fi
    [ "$(cat "$fixture/stop-args")" = $'one graceful\ntwo force\none force' ]
) > "$fixture/stop.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/stop.log"; bad "stop: -f anywhere, rm matching, stopped boxes skipped"; }

stop_modes_test() {
    regression_setup
    mkdir -p "$ROOT/vm"
    bash -c 'exec -a "$1" sleep 30' -- "file=$ROOT/vm/disk.qcow2,if=virtio" &
    vm_pid=$!
    trap 'kill "$vm_pid" 2>/dev/null || true; wait "$vm_pid" 2>/dev/null || true' EXIT
    echo "$vm_pid" > "$ROOT/vm/pid"
    touch "$ROOT/vm/ready"
    sleep 0.05
    ssh_plain_box() { echo "$*" >> "$fixture/stop-ssh"; }
    stop_box vm force 2> "$fixture/stop-force.log"
    [ ! -e "$fixture/stop-ssh" ]
    grep -q 'sending SIGTERM' "$fixture/stop-force.log"
    [ ! -e "$ROOT/vm/pid" ] && [ ! -e "$ROOT/vm/ready" ] && [ -f "$ROOT/vm/stopped" ]
    bash -c 'exec -a "$1" sleep 30' -- "file=$ROOT/vm/disk.qcow2,if=virtio" &
    vm_pid=$!
    echo "$vm_pid" > "$ROOT/vm/pid"
    sleep 0.05
    ssh_plain_box() { echo "$*" >> "$fixture/stop-ssh"; kill "$vm_pid"; }
    stop_box vm 2> "$fixture/stop-graceful.log"
    grep -q 'sudo poweroff' "$fixture/stop-ssh"
    grep -q 'waiting up to 90s for guest shutdown' "$fixture/stop-graceful.log"
    if grep -q SIGTERM "$fixture/stop-graceful.log"; then exit 1; fi
    [ ! -e "$ROOT/vm/pid" ] && [ -f "$ROOT/vm/stopped" ]
}
regression "stop -f signals qemu without a guest shutdown; graceful asks first" stop_modes_test

(
    set -e
    ROOT="$fixture/pruning"
    mkdir -p "$ROOT"/{old,young,busy,failed,stopped,recent}
    for n in old young busy failed; do touch "$ROOT/$n/ready"; done
    for n in stopped recent; do touch "$ROOT/$n/stopped"; done
    touch -d '5 hours ago' "$ROOT/old/ready" "$ROOT/busy/ready" "$ROOT/failed/ready"
    touch -d '3 hours ago' "$ROOT/stopped/stopped"
    running() { [[ "$1" != stopped && "$1" != recent ]]; }
    session_markers() {
        case "$1" in busy) echo 123;; failed) return 1;; esac
    }
    stop_box() { echo "$1" >> "$fixture/stopped-idle"; }
    remove_box() { echo "$1" >> "$fixture/pruned"; }
    if prune_boxes 2; then exit 1; fi
    [ "$(cat "$fixture/pruned")" = stopped ]
    [ "$(cat "$fixture/stopped-idle")" = old ]
) > "$fixture/prune.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/prune.log"; bad "prune age, grace, busy and failed count"; }

(
    set -e
    ROOT="$fixture/listing"
    mkdir -p "$ROOT/vm"
    echo $$ > "$ROOT/vm/pid"
    echo disk > "$ROOT/vm/disk.qcow2"
    running() { return 0; }
    session_markers() { echo 123; }
    output=$(list_boxes)
    [[ "$output" = NAME$'\t'STATUS$'\t'USE$'\t'RAM$'\t'DISK$'\t'PATH* ]]
    [[ "$output" = *$'running\tbusy\t'*KiB* ]]
    session_markers() { :; }
    [[ "$(list_boxes)" = *$'running\tidle\t'* ]]
    session_markers() { return 1; }
    [[ "$(list_boxes)" = *$'running\t?\t'* ]]
) > "$fixture/list.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/list.log"; bad "ls columns and marker states"; }

(
    ROOT="$fixture/leave"
    name=vm; sid=123; session_pid=""; locked=""
    mkdir -p "$ROOT/vm"
    echo disk > "$ROOT/vm/disk.qcow2"
    running() { return 0; }
    ssh_plain_box() { echo "$2" > "$fixture/leave-command"; }
    session_markers() { :; }
    stop_box() { touch "$fixture/stopped"; }
    leave_session
)
eq "last session preserves disk" "$(cat "$fixture/leave/vm/disk.qcow2")" disk
true_ "last session powers off" '[ -f "$fixture/stopped" ]'
eq "exit removes own marker" "$(cat "$fixture/leave-command")" \
    'sudo rm -f /run/qemubox/sess/123'
for mode in busy failed; do
    (
        name=vm; sid=123; session_pid=""; locked=""
        running() { return 0; }
        ssh_plain_box() { :; }
        session_markers() { [ "$mode" = busy ] && echo 456; }
        stop_box() { touch "$fixture/incorrect-stop-$mode"; }
        leave_session
    ) >/dev/null 2>&1
    false_ "$mode count keeps VM" '[ -f "$fixture/incorrect-stop-$mode" ]'
done

(
    set -e
    ROOT="$fixture/readiness"
    name=vm; mkdir -p "$ROOT/vm"
    echo 'serial failure evidence' > "$ROOT/vm/serial.log"
    QEMUBOX_READY_TIMEOUT=1
    ssh_plain_box() { :; }
    if wait_ready vm session 2> "$fixture/timeout"; then exit 1; fi
    grep -q 'serial failure evidence' "$fixture/timeout"
    touch "$ROOT/vm/ready"
    wait_ready vm session
    lock_box vm
    (
        locked=""
        lock_box vm
        echo acquired > "$fixture/acquired"
        unlock_box
    ) &
    waiter=$!
    sleep 0.1
    [ ! -f "$fixture/acquired" ]
    unlock_box
    wait "$waiter"
    [ -f "$fixture/acquired" ]
) > "$fixture/ready.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/ready.log"; bad "ready gate, serial tail and lock wait"; }
