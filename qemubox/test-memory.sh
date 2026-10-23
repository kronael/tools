eq 'default guest swap MiB' "$SWAP" 16384

swap_config_test() {
    regression_setup
    local value
    for value in '' -1 1G 1.5 ' 16' 1000000000
    do
        SWAP="$value"
        if ensure_box invalidswap 2> "$fixture/swap-error"
        then
            return 1
        else
            [[ "$?" = 2 ]]
        fi
        [[ ! -e "$ROOT/invalidswap" ]]
        grep -q QEMUBOX_SWAP "$fixture/swap-error"
    done
    if QEMUBOX_SWAP=bad QEMUBOX_HOME="$ROOT/invalid-cli" \
        bash "$here/qemubox" -T exec true 2> "$fixture/swap-error"
    then
        return 1
    else
        [[ "$?" = 2 ]]
    fi
    [[ ! -e "$ROOT/invalid-cli" ]]
    SWAP=16384 untrusted="" ensure_box swapdefault
    [[ "$(cat "$ROOT/swapdefault/config/swap")" = 16384 ]]
    SWAP=0008 untrusted="" ensure_box swapdecimal
    [[ "$(cat "$ROOT/swapdecimal/config/swap")" = 8 ]]
    SWAP=0 untrusted="" ensure_box swapdisabled
    [[ "$(cat "$ROOT/swapdisabled/config/swap")" = 0 ]]
}
regression 'swap settings validate before box files and serialize whole MiB' \
    swap_config_test

guest_swap_test() {
    local dir="$fixture/guest-swap"
    mkdir -p "$dir/config" "$dir/disk"
    awk '/^setup_swap\(\)/ {emit=1}
        /^reclaim_memory_loop\(\)/ {exit} emit {print}' "$here/guest-init" |
        sed "s|/run/qemubox/config|$dir/config|g;
             s|/\.qemubox|$dir/disk|g" > "$dir/swap-init"
    source "$dir/swap-init"
    findmnt() { echo "${swap_fs:-ext4}"; }
    df() { printf '1B-blocks\n8388608\n'; }
    mkswap() {
        printf '%s\n' "$*" >> "$dir/formatted"
        command mkswap "$@"
    }
    swapon() { printf '%s\n' "$*" >> "$dir/enabled"; }
    echo 0 > "$dir/config/swap"
    setup_swap
    [[ ! -e "$dir/disk/swap" && ! -e "$dir/enabled" ]]
    echo bad > "$dir/config/swap"
    if setup_swap 2> "$dir/error"
    then
        return 1
    fi
    echo 8 > "$dir/config/swap"
    if setup_swap 2> "$dir/error"
    then
        return 1
    fi
    grep -q 'leaves no filesystem capacity' "$dir/error"
    echo 1 > "$dir/config/swap"
    if swap_fs=overlay setup_swap 2> "$dir/error"
    then
        return 1
    fi
    grep -q 'requires direct ext4' "$dir/error"
    setup_swap
    [[ "$(stat -c %s "$dir/disk/swap")" = 1048576 ]]
    [[ "$(stat -c %a "$dir/disk/swap")" = 600 ]]
    [[ "$(stat -c %b "$dir/disk/swap")" -ge 2048 ]]
    [[ ! -e "$dir/disk/swap.new" ]]
    setup_swap
    [[ "$(wc -l < "$dir/formatted")" = 1 ]]
    [[ "$(wc -l < "$dir/enabled")" = 2 ]]
    echo 2 > "$dir/config/swap"
    if setup_swap 2> "$dir/error"
    then
        return 1
    fi
    grep -q 'stores 1048576 bytes; requested 2097152' "$dir/error"
    [[ "$(wc -l < "$dir/enabled")" = 2 ]]
    echo 0 > "$dir/config/swap"
    setup_swap
    [[ "$(stat -c %s "$dir/disk/swap")" = 1048576 ]]
    rm "$dir/disk/swap"
    echo 1 > "$dir/config/swap"
    fallocate() { echo 'fallocate: No space left on device' >&2; return 28; }
    if setup_swap 2> "$dir/error"
    then
        return 1
    fi
    grep -q 'No space left on device' "$dir/error"
    [[ ! -e "$dir/disk/swap" ]]
    [[ "$(wc -l < "$dir/formatted")" = 1 ]]
    [[ "$(wc -l < "$dir/enabled")" = 2 ]]
}
regression 'guest swap allocates extents once and preserves size and ENOSPC' \
    guest_swap_test

guest_tmp_size_test() {
    local dir="$fixture/guest-tmp"
    mkdir -p "$dir"
    awk '/^tmp_kib=/ {emit=1} emit {print}
        /^mount -t tmpfs .*tmpfs \/tmp$/ {exit}' "$here/guest-init" |
        sed "s|/proc/meminfo|$dir/meminfo|" > "$dir/tmp-init"
    mount() { printf '%s\n' "$*"; }
    export -f mount
    printf 'MemTotal: 1048576 kB\nSwapTotal: 4194304 kB\n' > "$dir/meminfo"
    [[ "$(bash -e "$dir/tmp-init")" = \
        '-t tmpfs -o rw,exec,mode=1777,size=3932160k tmpfs /tmp' ]]
    printf 'MemTotal: 1048577 kB\nSwapTotal: 0 kB\n' > "$dir/meminfo"
    [[ "$(bash -e "$dir/tmp-init")" = \
        '-t tmpfs -o rw,exec,mode=1777,size=786432k tmpfs /tmp' ]]
}
regression 'tmpfs uses three quarters of RAM and active swap in whole KiB' \
    guest_tmp_size_test

guest_reclaim_test() {
    local dir="$fixture/guest-reclaim" value
    mkdir -p "$dir/cgroup"
    printf 'MemTotal: 1048576 kB\n' > "$dir/meminfo"
    awk '/^reclaim_memory_loop\(\)/ {emit=1}
        /^shutdown\(\)/ {exit} emit {print}' "$here/guest-init" |
        sed "s|/sys/fs/cgroup/qemubox|$dir/cgroup|g;
             s|/proc/meminfo|$dir/meminfo|g" > "$dir/reclaim-init"
    source "$dir/reclaim-init"
    sleep() {
        [[ "$1" = 60 ]]
        ((ticks += 1))
        ((ticks <= 1))
    }
    for value in 536870911 536870912 536875008 2147483648
    do
        echo "$value" > "$dir/cgroup/memory.current"
        : > "$dir/cgroup/memory.reclaim"
        ticks=0 reclaim_memory_loop
        case "$value" in
            536870911|536870912) [[ ! -s "$dir/cgroup/memory.reclaim" ]] ;;
            536875008) [[ "$(cat "$dir/cgroup/memory.reclaim")" = 4096 ]] ;;
            2147483648) [[ "$(cat "$dir/cgroup/memory.reclaim")" = 1073741824 ]] ;;
        esac
    done
    printf() {
        if [[ "$2" = 1073741824 ]]
        then
            echo 2147479552 > "$dir/cgroup/memory.current"
            echo 'printf: write error: Resource temporarily unavailable' >&2
            return 1
        fi
        builtin printf "$@"
    }
    ticks=0 reclaim_memory_loop 2> "$dir/shortfall"
    grep -q 'Resource temporarily unavailable' "$dir/shortfall"
    grep -q 'shortfall: requested=1073741824 before=2147483648 after=2147479552' \
        "$dir/shortfall"
    unset -f printf
    rm "$dir/cgroup/memory.reclaim"
    ln -s /dev/full "$dir/cgroup/memory.reclaim"
    if ticks=0 reclaim_memory_loop 2> "$dir/error"
    then
        return 1
    fi
    grep -q 'No space left on device' "$dir/error"
    grep -q 'memory.reclaim failed:' "$dir/error"
    ! grep -q shortfall "$dir/error"
}
regression 'reclaim bounds requests and separates EAGAIN from control errors' \
    guest_reclaim_test

guest_workload_test() {
    local dir="$fixture/guest-workload" args
    mkdir -p "$dir/cgroup" "$dir/bin"
    echo 'memory cpu pids' > "$dir/cgroup/cgroup.controllers"
    awk '/^read -ra controllers/ {emit=1} emit {print}
        /^docker_pid=\$!/ {exit}' "$here/guest-init" |
        sed "s|/sys/fs/cgroup|$dir/cgroup|g;
             s|/\.qemubox/|$dir/disk/|g;
             s|/var/lib/|$dir/var/|g" > "$dir/workload-init"
    printf '\nwait "$docker_pid"\n' >> "$dir/workload-init"
    mount() { :; }
    cat > "$dir/bin/dockerd" <<'EOF'
#!/bin/sh
printf '%s\n' "$$" "$*" > "$QEMUBOX_TEST_DOCKER"
EOF
    chmod +x "$dir/bin/dockerd"
    export -f mount
    PATH="$dir/bin:$PATH" QEMUBOX_TEST_DOCKER="$dir/daemon" \
        bash -e "$dir/workload-init"
    [[ "$(cat "$dir/cgroup/cgroup.subtree_control")" = \
        '+memory +cpu +pids ' ]]
    [[ "$(cat "$dir/cgroup/qemubox/cgroup.subtree_control")" = \
        '+memory +cpu +pids ' ]]
    [[ -d "$dir/cgroup/qemubox/docker" ]]
    [[ -d "$dir/cgroup/qemubox/sessions" ]]
    [[ "$(cat "$dir/cgroup/qemubox/services/cgroup.procs")" = \
        "$(head -1 "$dir/daemon")" ]]
    args='--exec-opt native.cgroupdriver=cgroupfs '
    args+='--cgroup-parent=/qemubox/docker --shutdown-timeout=3'
    grep -Fxq -- "$args" "$dir/daemon"
    [[ ! -e "$dir/cgroup/qemubox/cgroup.procs" ]]
}
regression 'Docker daemon joins workloads while their parent stays empty' \
    guest_workload_test
