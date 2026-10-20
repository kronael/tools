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
    stop_boxes -a 2> "$fixture/stop-skipped"
    [ "$(cat "$fixture/stop-args")" = $'one graceful\ntwo force\none force\none graceful\ntwo graceful' ]
    grep -q 'qemubox-down is not running' "$fixture/stop-skipped"
) > "$fixture/stop.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/stop.log"; bad "stop: -f anywhere, -a, rm matching, stopped boxes skipped"; }

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
    [ ! -e "$ROOT/vm/pid" ]
    [ ! -e "$ROOT/vm/ready" ]
    [ -f "$ROOT/vm/stopped" ]
    bash -c 'exec -a "$1" sleep 30' -- "file=$ROOT/vm/disk.qcow2,if=virtio" &
    vm_pid=$!
    echo "$vm_pid" > "$ROOT/vm/pid"
    sleep 0.05
    ssh_plain_box() { echo "$*" >> "$fixture/stop-ssh"; kill "$vm_pid"; }
    stop_box vm 2> "$fixture/stop-graceful.log"
    grep -q 'sudo poweroff' "$fixture/stop-ssh"
    grep -q 'waiting up to 90s for guest shutdown' "$fixture/stop-graceful.log"
    if grep -q SIGTERM "$fixture/stop-graceful.log"; then exit 1; fi
    [ ! -e "$ROOT/vm/pid" ]
    [ -f "$ROOT/vm/stopped" ]
    bash -c 'exec -a "$1" sleep 30' -- "file=$ROOT/vm/disk.qcow2,if=virtio" &
    vm_pid=$!
    echo "$vm_pid" > "$ROOT/vm/pid"
    sleep 0.05
    ssh_plain_box() { :; }
    sleep() { :; }
    stop_box vm 2> "$fixture/stop-escalate.log"
    grep -q 'waiting up to 90s' "$fixture/stop-escalate.log"
    grep -q 'sending SIGTERM' "$fixture/stop-escalate.log"
    if grep -q SIGKILL "$fixture/stop-escalate.log"; then exit 1; fi
    [ ! -e "$ROOT/vm/pid" ]
    [ -f "$ROOT/vm/stopped" ]
    bash -c 'trap "" TERM; exec -a "$1" sleep 30' -- "file=$ROOT/vm/disk.qcow2,if=virtio" &
    vm_pid=$!
    echo "$vm_pid" > "$ROOT/vm/pid"
    command sleep 0.05
    stop_box vm force 2> "$fixture/stop-kill.log"
    grep -q 'sending SIGTERM' "$fixture/stop-kill.log"
    grep -q 'sending SIGKILL' "$fixture/stop-kill.log"
    [ ! -e "$ROOT/vm/pid" ]
    [ -f "$ROOT/vm/stopped" ]
}
regression "stop -f signals qemu without a guest shutdown; graceful asks first" stop_modes_test

(
    set -e
    sleep() { :; }
    running() { return 0; }
    if wait_stopped vm 3; then exit 1; fi
    running() { return 1; }
    wait_stopped vm 3
) > "$fixture/wait.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/wait.log"; bad "wait_stopped reports a timeout"; }

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
    if prune_boxes; then exit 1; fi
    [ ! -e "$fixture/pruned" ]
    [ "$(cat "$fixture/stopped-idle")" = old ]
) > "$fixture/prune.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/prune.log"; bad "prune grace, busy and failed count; removes no VM"; }

(
    set -e
    ROOT="$fixture/rm-stopped"
    mkdir -p "$ROOT"/{old,recent,up,base}
    touch "$ROOT/old/stopped" "$ROOT/recent/stopped"
    touch -d '3 hours ago' "$ROOT/old/stopped"
    running() { [ "$1" = up ]; }
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
    running() { [ "$1" = "$up" ]; }
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
    echo $$ > "$ROOT/vm/pid"
    echo disk > "$ROOT/vm/disk.qcow2"
    running() { return 0; }
    session_markers() { echo 123; }
    ssh_plain_box() { printf '%s\n' 'x[$(touch "$fixture/pwned")0]' 1 1 1; }
    list_boxes > /dev/null
    [ ! -e "$fixture/pwned" ]
    ssh_plain_box() { printf '%s\n' 100 40 30 10; }
    [[ "$(list_boxes)" = *$'\t60K\t20K\t10K\t'* ]]
    unset -f ssh_plain_box
    output=$(list_boxes)
    [[ "$output" = NAME$'\t'STATUS$'\t'USE$'\t'RAM$'\t'USED$'\t'CACHE$'\t'TMPFS$'\t'DISK$'\t'PATH* ]]
    [[ "$output" = *$'running\tbusy\t'*[0-9KMG]* ]]
    session_markers() { :; }
    [[ "$(list_boxes)" = *$'running\tidle\t'* ]]
    session_markers() { return 1; }
    [[ "$(list_boxes)" = *$'running\t?\t'* ]]
) > "$fixture/list.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/list.log"; bad "ls columns and marker states"; }

(
    ROOT="$fixture/leave"
    name=vm; sid=123; session_pid=""; locked=""
    LINGER=0
    mkdir -p "$ROOT/vm"
    echo disk > "$ROOT/vm/disk.qcow2"
    running() { return 0; }
    ssh_plain_box() { echo "$2" > "$fixture/leave-command"; }
    session_markers() { :; }
    stop_box() { touch "$fixture/stopped"; }
    leave_session
) 2> "$fixture/leave.err"
eq "last session preserves disk" "$(cat "$fixture/leave/vm/disk.qcow2")" disk
true_ "QEMUBOX_LINGER=0 powers off at once" '[ -f "$fixture/stopped" ]'
false_ "QEMUBOX_LINGER=0 stamps no idle" '[ -e "$fixture/leave/vm/idle" ]'
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
    name=vm; sid=123; session_pid=""; locked=""
    running() { [ ! -e "$fixture/guest-down" ]; }
    ssh_plain_box() { echo "kex_exchange_identification: reset" >&2; return 255; }
    sleep() { touch "$fixture/guest-down"; }
    stop_box() { touch "$fixture/incorrect-stop-poweroff"; }
    leave_session
) 2> "$fixture/poweroff.err"
eq "a guest poweroff ends the session cleanly" "$?" 0
true_ "a guest poweroff is reported as such" 'grep -q "powered off during the session" "$fixture/poweroff.err"'
false_ "a guest poweroff hides the ssh error" 'grep -q "kex_exchange" "$fixture/poweroff.err"'
false_ "a guest poweroff is not a kept VM" 'grep -q "keeping qemubox-vm running" "$fixture/poweroff.err"'
false_ "a guest poweroff signals nothing" '[ -f "$fixture/incorrect-stop-poweroff" ]'
(
    name=vm; sid=123; session_pid=""; locked=""
    running() { return 0; }
    ssh_plain_box() { echo "kex_exchange_identification: reset" >&2; return 255; }
    sleep() { :; }
    stop_box() { touch "$fixture/incorrect-stop-marker"; }
    leave_session
) 2> "$fixture/marker.err"
eq "a failed marker removal on a live VM exits 1" "$?" 1
true_ "a failed marker removal keeps the VM" 'grep -q "keeping qemubox-vm running" "$fixture/marker.err"'
true_ "a failed marker removal shows the ssh error" 'grep -q "kex_exchange" "$fixture/marker.err"'
false_ "a failed marker removal signals nothing" '[ -f "$fixture/incorrect-stop-marker" ]'

(
    set -e
    ROOT="$fixture/token"
    mkdir -p "$ROOT/vm"
    if has_idle_token vm mine; then exit 1; fi
    echo mine > "$ROOT/vm/idle"
    has_idle_token vm mine
    if has_idle_token vm newer; then exit 1; fi
) > "$fixture/token.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/token.log"; bad "idle stamp holds one token"; }

for scen in superseded retry busy stale down
do
    (
        ROOT="$fixture/linger-$scen"
        mkdir -p "$ROOT/vm"
        echo mine > "$ROOT/vm/idle"
        LINGER=1
        sleep() { command sleep 0.05; }
        running() { return 0; }
        session_markers() { :; }
        stop_box() { touch "$fixture/linger-$scen-stopped"; }
        case "$scen" in
            superseded) echo newer > "$ROOT/vm/idle" ;;
            retry|busy)
                session_markers() {
                    [ -e "$ROOT/retried" ] || { touch "$ROOT/retried"; return 1; }
                    [ "$scen" = retry ] || echo 456
                } ;;
            stale)
                touch -d '5 hours ago' "$ROOT/vm/idle"
                session_markers() { return 1; } ;;
            down) running() { return 1; } ;;
        esac
        stop_after_linger vm mine
        echo "rc=$?"
    ) > "$fixture/linger-$scen.log" 2>&1
done
false_ "superseded check leaves the VM" '[ -e "$fixture/linger-superseded-stopped" ]'
true_ "superseded check says so" \
    'grep -q "stamped idle again" "$fixture/linger-superseded.log"'
true_ "failed count retries, then powers off" '[ -e "$fixture/linger-retry-stopped" ]'
true_ "retry is logged" 'grep -q "retrying in 1s" "$fixture/linger-retry.log"'
false_ "busy after a retry leaves the VM" '[ -e "$fixture/linger-busy-stopped" ]'
true_ "busy is logged" 'grep -q "is busy; leaving it" "$fixture/linger-busy.log"'
false_ "count failing 4h after the last exit gives up" \
    '[ -e "$fixture/linger-stale-stopped" ]'
true_ "giving up is logged" 'grep -q "giving up" "$fixture/linger-stale.log"'
eq "giving up returns 1" "$(tail -1 "$fixture/linger-stale.log")" "rc=1"
false_ "stopped VM is left alone" '[ -e "$fixture/linger-down-stopped" ]'

(
    ROOT="$fixture/leave-linger"
    name=vm; sid=123; session_pid=""; locked=""
    LINGER=1
    mkdir -p "$ROOT/vm"
    running() { return 0; }
    ssh_plain_box() { :; }
    session_markers() { :; }
    stop_box() { touch "$fixture/linger-stopped"; }
    leave_session
) 2> "$fixture/leave-linger.err"
false_ "last session lingers instead of stopping at once" '[ -f "$fixture/linger-stopped" ]'
true_ "last session stamps idle with a token" '[ -s "$fixture/leave-linger/vm/idle" ]'
true_ "exit announces the linger" 'grep -q "powers off after 1s" "$fixture/leave-linger.err"'
for ((i = 0; i < 300; i++))
do
    [ ! -f "$fixture/linger-stopped" ] || break
    sleep 0.01
done
true_ "detached check powers off after the linger" '[ -f "$fixture/linger-stopped" ]'
true_ "detached check logs its decision" \
    'grep -q "powering off qemubox-vm" "$fixture/leave-linger/vm/idle.log"'

(
    set -e
    ROOT="$fixture/leave-nostderr"
    name=vm; sid=123; session_pid=""; locked=""
    LINGER=1
    mkdir -p "$ROOT/vm"
    running() { return 0; }
    ssh_plain_box() { :; }
    session_markers() { :; }
    stop_box() { touch "$fixture/nostderr-stopped"; }
    leave_session
) 2>/dev/full
for ((i = 0; i < 300; i++))
do
    [ ! -f "$fixture/nostderr-stopped" ] || break
    sleep 0.01
done
true_ "last session with a dead stderr still arms the idle stop" \
    '[ -f "$fixture/nostderr-stopped" ]'

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
