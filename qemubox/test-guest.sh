guest_mounts_test() {
    local dir="$fixture/guest-mounts" path
    mkdir -p "$dir"/{config,tmp,existing,project}
    chmod 750 "$dir/existing"
    touch "$dir/project/.qemuboxrc"
    printf 'qbx0\t/host/rw\t%s/existing/new/nested\trw\n' "$dir" \
        > "$dir/config/mounts"
    printf 'qbx1\t/host/ro\t%s/project\tro\n' "$dir" >> "$dir/config/mounts"
    printf 'cfg\t/host/config\t/run/qemubox/config\tro\n' \
        >> "$dir/config/mounts"
    printf 'root\t/host/rootfs\t/.qemubox/lower\tro\n' \
        >> "$dir/config/mounts"
    mkdir -p "$dir/project/space dir/node_modules"
    printf '%s\0' tmpfs "$dir/project/space dir/node_modules" \
        > "$dir/config/ephemeral"
    awk '/^tmp_kib=/ {emit=1}
        /^mkdir -p .*home_dir/ {exit} emit {print}' "$here/guest-init" |
        sed "s|/tmp/|$dir/tmp/|g;
             s| tmpfs /tmp$| tmpfs $dir/tmp|;
             s|/var/lib/qemubox|$dir/disk|g;
             s|/run/qemubox/config|$dir/config|g" > "$dir/mounts-init"
    mount() { printf '%s\n' "$*" >> "$QEMUBOX_TEST_MOUNTS"; }
    export -f mount
    export QEMUBOX_TEST_MOUNTS="$dir/mounts"
    user_uid=$(id -u) user_gid=$(id -g) bash -e "$dir/mounts-init"
    grep -Fxq -- "-t virtiofs -o rw qbx0 $dir/existing/new/nested" \
        "$dir/mounts"
    grep -Fxq -- "-t virtiofs -o ro qbx1 $dir/project" "$dir/mounts"
    grep -Fxq -- "--bind /dev/null $dir/project/.qemuboxrc" "$dir/mounts"
    grep -Fxq -- "-o remount,bind,ro $dir/project/.qemuboxrc" "$dir/mounts"
    [[ "$(stat -c %a "$dir/existing")" = 750 ]]
    [[ "$(stat -c %a "$dir/existing/new")" = 755 ]]
    [[ "$(stat -c %u:%g "$dir/existing/new")" = "$(id -u):$(id -g)" ]]
    [[ "$(grep -c -- '-t tmpfs ' "$dir/mounts")" = 1 ]]
    ! grep -q -- ' ro cfg ' "$dir/mounts"
    ! grep -q -- ' ro root ' "$dir/mounts"
    path=$(tail -1 "$dir/mounts")
    [[ "$path" == "--bind $dir/tmp/qemubox-builds/"* ]]
    [[ "$path" == *" $dir/project/space dir/node_modules" ]]
    : > "$dir/mounts"
    printf '%s\0' disk "$dir/project/space dir/node_modules" \
        > "$dir/config/ephemeral"
    user_uid=$(id -u) user_gid=$(id -g) bash -e "$dir/mounts-init"
    [[ "$(tail -1 "$dir/mounts")" == "--bind $dir/disk/builds/"* ]]
    printf '%s\0' tmpfs > "$dir/config/ephemeral"
    : > "$dir/mounts"
    user_uid=$(id -u) user_gid=$(id -g) bash -e "$dir/mounts-init"
    ! grep -q qemubox-builds "$dir/mounts"
    mount() { return 32; }
    export -f mount
    if user_uid=$(id -u) user_gid=$(id -g) bash -e "$dir/mounts-init"
    then
        return 1
    else
        [[ "$?" = 32 ]]
    fi
}
regression 'guest mounts preserve parent modes, rc masks and build backing' \
    guest_mounts_test

guest_home_test() {
    local dir="$fixture/guest-home" rel
    mkdir -p "$dir"/{config,etc,mnt/qemubox-home/.gnupg,mnt/qemubox-history,tmp}
    mkdir -p "$dir/home/.claude/sessions"
    chmod 700 "$dir/home/.claude/sessions"
    printf 'public key\n' > "$dir/config/authorized_keys"
    printf 'guest guidance\n' > "$dir/config/CLAUDE.md"
    for rel in .claude.json .gitconfig .gnupg/pubring.kbx .gnupg/pubring.gpg
    do
        printf 'host config\n' > "$dir/mnt/qemubox-home/$rel"
    done
    touch "$dir/mnt/qemubox-history/history"
    awk '/^mkdir -p .*home_dir.*ssh/ {emit=1}
        /^ssh-keygen -A/ {exit} emit {print}' "$here/guest-init" |
        sed "s|/run/qemubox/config|$dir/config|g;
             s|/etc/|$dir/etc/|g;
             s|/mnt/|$dir/mnt/|g;
             s|/tmp/host-claude.json|$dir/tmp/host-claude.json|g" \
        > "$dir/home-init"
    mount() { printf '%s\n' "$*" >> "$QEMUBOX_TEST_MOUNTS"; }
    export -f mount
    export QEMUBOX_TEST_MOUNTS="$dir/mounts"
    username=guest user_uid=$(id -u) user_gid=$(id -g) \
        home_dir="$dir/home" mode=trusted bash -e "$dir/home-init"
    [[ "$(stat -c %a "$dir/home/.claude/sessions")" = 700 ]]
    [[ "$(stat -c %a "$dir/home/.ssh/authorized_keys")" = 600 ]]
    [[ "$(stat -c %a "$dir/home/.ssh")" = 700 ]]
    [[ "$(stat -c %a "$dir/home/.gnupg")" = 700 ]]
    cmp "$dir/config/CLAUDE.md" "$dir/etc/claude-code/CLAUDE.md"
    for rel in .gitconfig .gnupg/pubring.kbx .gnupg/pubring.gpg
    do
        [[ "$(readlink "$dir/home/$rel")" = "$dir/mnt/qemubox-home/$rel" ]]
    done
    [[ "$(readlink "$dir/tmp/host-claude.json")" = \
        "$dir/mnt/qemubox-home/.claude.json" ]]
    for rel in .bash_history .zsh_history
    do
        grep -Fxq -- "--bind $dir/mnt/qemubox-history/history $dir/home/$rel" \
            "$dir/mounts"
    done
    local session_mount="-t tmpfs -o mode=0700,uid=$(id -u),gid=$(id -g)"
    grep -Fxq -- "$session_mount tmpfs $dir/home/.claude/sessions" \
        "$dir/mounts"
    grep -Fxq 'guest - memlock unlimited' \
        "$dir/etc/security/limits.d/90-qemubox.conf"
    : > "$dir/mounts"
    username=guest user_uid=$(id -u) user_gid=$(id -g) \
        home_dir="$dir/untrusted" mode=untrusted bash -e "$dir/home-init"
    [[ ! -e "$dir/untrusted/.claude/sessions" ]]
    [[ ! -e "$dir/untrusted/.gitconfig" ]]
    [[ ! -s "$dir/mounts" ]]
}
regression 'guest home shares guidance and history, with private sessions' \
    guest_home_test

guest_services_test() (
    local dir="$fixture/guest-services" runner
    mkdir -p "$dir"/{bin,cgroup,sessions}
    echo 0 > "$dir/cgroup/memory.current"
    cat > "$dir/bin/docker" <<'EOF'
#!/bin/sh
test -f "$QEMUBOX_TEST_SERVICES/docker-ready"
EOF
    cat > "$dir/bin/sshd" <<'EOF'
#!/bin/sh
test "$1" != -t || exit 0
printf '%s\n' "$$" > "$QEMUBOX_TEST_SERVICES/sshd-pid"
exec sleep 30
EOF
    chmod +x "$dir/bin/"*
    printf '%s\n' 'set -Eeuo pipefail' \
        'sshd_pid=""' \
        'reclaim_pid=""' \
        'sleep 30 & docker_pid=$!' \
        'trap '\''kill "$docker_pid" "$sshd_pid" "$reclaim_pid" 2>/dev/null || true'\'' EXIT' \
        > "$dir/services-init"
    awk '/^reclaim_memory_loop\(\)/ {emit=1}
        /^shutdown\(\)/ {exit} emit {print}' "$here/guest-init" |
        sed "s|/sys/fs/cgroup/qemubox|$dir/cgroup|g" \
        >> "$dir/services-init"
    awk '/^ssh-keygen -A/ {emit=1} emit {print}' "$here/guest-init" |
        sed "s|/usr/sbin/sshd|$dir/bin/sshd|g;
             s|/sys/fs/cgroup/qemubox/sessions|$dir/sessions|g;
             s|/run/qemubox/ready|$dir/ready|g" >> "$dir/services-init"
    ssh-keygen() { :; }
    sleep() {
        if [[ "$1" = 60 ]]
        then
            command sleep 0.05
        else
            command sleep "$@"
        fi
    }
    export -f ssh-keygen sleep
    export QEMUBOX_TEST_SERVICES="$dir"
    PATH="$dir/bin:$PATH" bash "$dir/services-init" > "$dir/output" 2>&1 &
    runner=$!
    trap 'kill "$runner" 2>/dev/null || true
        wait "$runner" 2>/dev/null || true' EXIT
    for ((i=0; i<100; i++))
    do
        [[ ! -f "$dir/sshd-pid" ]] || break
        sleep 0.01
    done
    [[ -s "$dir/sshd-pid" && ! -e "$dir/ready" ]]
    [[ "$(cat "$dir/sessions/cgroup.procs")" = "$(cat "$dir/sshd-pid")" ]]
    touch "$dir/docker-ready"
    for ((i=0; i<100; i++))
    do
        [[ ! -f "$dir/ready" ]] || break
        sleep 0.01
    done
    [[ -f "$dir/ready" ]]
    kill -TERM "$(cat "$dir/sshd-pid")"
    if wait "$runner"
    then
        return 1
    else
        [[ "$?" = 1 ]]
    fi
    grep -Fxq 'qemubox: ready' "$dir/output"
    grep -q 'required service exited with status ' "$dir/output"
    rm "$dir/ready"
    echo 9223372036854775807 > "$dir/cgroup/memory.current"
    ln -s /dev/full "$dir/cgroup/memory.reclaim"
    PATH="$dir/bin:$PATH" bash "$dir/services-init" > "$dir/output" 2>&1 &
    runner=$!
    if wait "$runner"
    then
        return 1
    else
        [[ "$?" = 1 ]]
    fi
    grep -q 'No space left on device' "$dir/output"
    grep -q 'memory.reclaim failed:' "$dir/output"
    grep -q 'required service exited with status 1' "$dir/output"
    trap - EXIT
)
regression 'Docker readiness and service exits govern guest supervision' \
    guest_services_test
