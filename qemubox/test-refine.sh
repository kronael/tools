trust_modes() {
    untrusted=""
    ensure_box trusted
    [ "$(cat "$ROOT/trusted/trust")" = trusted ]
    untrusted=1
    if ensure_box trusted 2> "$fixture/trust-error"; then exit 1; fi
    grep -q -- '-n.*qemubox rm' "$fixture/trust-error"
    ensure_box untrusted
    untrusted=""
    if ensure_box untrusted; then exit 1; fi
    rm "$ROOT/trusted/trust"
    if ensure_box trusted; then exit 1; fi
}
trust_test() { regression_setup; trust_modes; }
regression "disk trust refuses both mode changes and unmarked disks" trust_test

markers_test() {
    regression_setup
    sleep 30 &
    dead=$!
    kill "$dead"; wait "$dead" || true
    ssh_plain_box() {
        if flock -n "$ROOT/.locks/vm" true; then return 1; fi
        case "$2" in
            'sudo ls'*) printf '%s\n' "$$" "$dead" ;;
            *) echo "$2" > "$fixture/reaped" ;;
        esac
    }
    lock_box vm
    [ "$(session_markers vm)" = "$$" ]
    [ "$(cat "$fixture/reaped")" = "sudo rm -f /run/qemubox/sess/$dead" ]
    unlock_box
}
regression "dead session markers are removed under lock" markers_test

resume_test() {
    primary="$fixture/repo_with.dot+space name"
    slug="${primary//[^A-Za-z0-9]/-}"
    mkdir -p "$HOME/.claude/projects/$slug"
    touch "$HOME/.claude/projects/$slug/session.jsonl"
    tool_cmd claude; resume_session
    [ "${cmd[1]}" = --resume ]
}
regression "resume handles every nonalphanumeric path character" resume_test

base_test() {
    regression_setup
    mkdir -p "$ROOT/kept"
    echo used > "$ROOT/kept/image-id"
    touch "$ROOT/kept/stopped"
    for id in used stale; do
        for suffix in qcow2 vmlinuz initrd; do echo data > "$ROOT/base/$id.$suffix"; done
    done
    prune_boxes
    for suffix in qcow2 vmlinuz initrd; do
        [ ! -e "$ROOT/base/stale.$suffix" ]
        [ -f "$ROOT/base/fixture.$suffix" ] && [ -f "$ROOT/base/used.$suffix" ]
    done
}
regression "prune removes only unused noncurrent base sets" base_test

pid_test() {
    regression_setup
    mkdir -p "$ROOT/vm"
    echo $$ > "$ROOT/vm/pid"
    if running vm; then exit 1; fi
    bash -c 'exec -a "$1" sleep 30' -- "file=$ROOT/vm/disk.qcow2,if=virtio" &
    vm_pid=$!
    trap 'kill "$vm_pid"; wait "$vm_pid" 2>/dev/null || true' EXIT
    echo "$vm_pid" > "$ROOT/vm/pid"
    sleep 0.05
    running vm
}
regression "pidfile must refer to this VM disk" pid_test

half_box_test() {
    regression_setup
    mkdir -p "$ROOT/half"
    list_boxes > "$fixture/half-list" 2> "$fixture/half-error"
    [ ! -s "$fixture/half-error" ]
    grep -q $'stopped\tidle\t0KiB\t0KiB' "$fixture/half-list"
}
regression "ls accepts an unfinished box without du errors" half_box_test

missing_mount_test() {
    regression_setup
    gcloud_creds=1; untrusted=1; extra_dirs=()
    if assemble_mounts 2> "$fixture/mount-error"; then exit 1; fi
    grep -q 'Missing mount source:' "$fixture/mount-error"
}
regression "explicit missing gcloud mount fails loudly" missing_mount_test

plugins_test() {
    mkdir -p "$HOME/.claude/plugins"
    run_assemble
    [ "$(mount_mode "$HOME/.claude/plugins")" = ro ]
}
regression "plugins have a readonly 9p export" plugins_test

rc_test() {
    reset_mounts; dirs=("$PROJ"); no_copy=""
    ssh_plain_box() { echo "$2" >> "$fixture/rc-commands"; }
    mount_host_paths vm
    grep -F -- "$PROJ/.qemuboxrc" "$fixture/rc-commands" | grep -q 'remount,bind,ro'
}
regression "project rc is masked by a readonly bind" rc_test

status_test() {
    regression_setup
    mkdir -p "$ROOT/vm"
    echo 'guest login:' > "$ROOT/vm/serial.log"
    [[ "$(status_box vm)" = *boot=pending* ]]
}
regression "login prompt does not prove guest readiness" status_test

base_lock_test() {
    regression_setup
    untrusted=""
    qemu-img() {
        if flock -n "$ROOT/base/.lock" true; then return 1; fi
        touch "$dir/disk.qcow2"
    }
    ensure_box lockedbase
    flock -n "$ROOT/base/.lock" true
}
regression "base remains locked until the disk reference is recorded" base_lock_test

metadata_test() {
    regression_setup
    mkdir -p "$ROOT/vm"
    touch "$ROOT/vm/seed.iso" "$ROOT/vm/user-data" "$ROOT/vm/meta-data"
    if remove_box vm; then exit 1; fi
    [ -f "$ROOT/vm/seed.iso" ] && [ -f "$ROOT/vm/user-data" ] && [ -f "$ROOT/vm/meta-data" ]
}
regression "removal leaves unowned cloud metadata alone" metadata_test
