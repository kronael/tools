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
    local used stale legacy_used legacy_stale kernel_current kernel_stale
    printf -v used '%064d' 1
    printf -v stale '%064d' 2
    printf -v legacy_used '%064d' 7
    printf -v legacy_stale '%064d' 8
    printf -v kernel_current '%064d' 4
    printf -v kernel_stale '%064d' 5
    echo "$used" > "$ROOT/kept/image-id"
    touch "$ROOT/kept/stopped"
    for id in "$used" "$stale"
    do
        mkdir -p "$ROOT/base/$id/rootfs"
        echo data > "$ROOT/base/$id/rootfs/file"
    done
    mkdir -p "$fixture/foreign-rootfs"
    echo keep > "$fixture/foreign-rootfs/file"
    ln -s "$fixture/foreign-rootfs" "$ROOT/base/$(printf '%064d' 3)"
    mkdir -p "$ROOT/base/not-an-image"
    mkdir -p "$ROOT/legacy"
    echo "$legacy_used" > "$ROOT/legacy/image-id"
    for id in "$legacy_used" "$legacy_stale"
    do
        for suffix in qcow2 vmlinuz initrd
        do
            echo data > "$ROOT/base/$id.$suffix"
        done
    done
    for id in "$kernel_current" "$kernel_stale"
    do
        mkdir -p "$ROOT/base/kernel/$id"
        echo kernel > "$ROOT/base/kernel/$id/bzImage"
    done
    echo "$kernel_current" > "$ROOT/base/kernel/current"
    ln -s "$fixture/foreign-rootfs" \
        "$ROOT/base/kernel/$(printf '%064d' 6)"
    prune_boxes
    [ ! -e "$ROOT/base/$stale" ]
    [ -f "$ROOT/base/fixture/exported" ]
    [ -f "$ROOT/base/$used/rootfs/file" ]
    [ -f "$fixture/foreign-rootfs/file" ]
    [ -d "$ROOT/base/not-an-image" ]
    [ -f "$ROOT/base/kernel/fixture/bzImage" ]
    [ -f "$ROOT/base/kernel/$kernel_current/bzImage" ]
    [ ! -e "$ROOT/base/kernel/$kernel_stale" ]
    for suffix in qcow2 vmlinuz initrd
    do
        [ -f "$ROOT/base/$legacy_used.$suffix" ]
        [ ! -e "$ROOT/base/$legacy_stale.$suffix" ]
    done
}
regression "prune removes only unused noncurrent base sets" base_test

no_current_test() {
    regression_setup
    rm "$ROOT/base/current"
    prune_bases
    [ -f "$ROOT/base/fixture/exported" ]
}
regression "prune_bases without a current base does nothing" no_current_test

random_name_test() {
    regression_setup
    a=$(random_name)
    [ -d "$ROOT/$a" ]
    mkdir() { [ "$1" = -p ] || return 1; command mkdir "$@"; }
    if random_name 2> "$fixture/name-error"; then exit 1; fi
    grep -q 'no free random name' "$fixture/name-error"
}
regression "random_name reserves its dir and gives up when none is free" random_name_test

half_box_test() {
    regression_setup
    mkdir -p "$ROOT/half"
    list_boxes > "$fixture/half-list" 2> "$fixture/half-error"
    [ ! -s "$fixture/half-error" ]
    grep -q $'stopped\tidle\t0\t-\t-\t-\t0' "$fixture/half-list"
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
regression "plugins have a readonly virtiofs export" plugins_test

base_lock_test() {
    regression_setup
    untrusted=""
    mkfs.ext4() {
        if flock -n "$ROOT/base/.lock" true; then return 1; fi
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
    [ -f "$ROOT/vm/seed.iso" ]
    [ -f "$ROOT/vm/user-data" ]
    [ -f "$ROOT/vm/meta-data" ]
}
regression "removal leaves unowned cloud metadata alone" metadata_test
