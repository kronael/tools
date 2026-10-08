image_init="$fixture/image-init"
awk '/^RUN printf/{block=$0;next} {block=block ORS $0}
    / > \/usr\/local\/bin\/qemubox-init &&/{print block}' "$here/../dockbox/Dockerfile" |
    sed '1s/^RUN //; s|> /usr/local/bin/qemubox-init.*|> "$image_init"|' > "$fixture/extract-init"
source "$fixture/extract-init"

sshd_test() {
    grep -q "'StreamLocalBindUnlink yes'" "$here/../dockbox/Dockerfile"
}
regression "guest sshd replaces stale Unix sockets" sshd_test

docker_cli_test() {
    sed '/^FROM dockbox AS vm/,$d' "$here/../dockbox/Dockerfile" | grep -qw docker-cli
}
regression "both images install docker-cli" docker_cli_test

timezone_test() {
    regression_setup
    untrusted=""
    ensure_box timezone
    [ "$(sed -n '6p' "$ROOT/timezone/config/identity")" = Etc/UTC ]
    mkdir -p "$fixture/zone/etc" "$fixture/zone/run/qemubox/config"
    cp "$ROOT/timezone/config/identity" "$fixture/zone/run/qemubox/config/identity"
    sed '/^passwd_entry=/,$d' "$image_init" |
        sed "s|/etc/|$fixture/zone/etc/|g; s|/run/|$fixture/zone/run/|g; s|/proc/sys/kernel/hostname|/dev/null|g" > "$fixture/zone-init"
    modprobe() { :; }; mount() { :; }
    export -f modprobe mount
    bash "$fixture/zone-init"
    [ "$(readlink "$fixture/zone/etc/localtime")" = /usr/share/zoneinfo/Etc/UTC ]
    ! grep -q '^RUN for key in TZ ' "$here/../dockbox/Dockerfile"
}
regression "identity and init set the UTC time zone" timezone_test

groups_test() {
    mkdir -p "$fixture/groups"
    printf '%s\n' 'systemd-journal:x:998:journaluser' 'wheel:x:10:other' > "$fixture/groups/group"
    sed -n '/^for group in /,/^done/p' "$image_init" |
        sed "s|/etc/group|$fixture/groups/group|g" > "$fixture/group-init"
    getent() {
        awk -F: -v key="$2" '$1==key || $3==key {found=1;print} END {exit !found}' "$fixture/groups/group"
    }
    export fixture
    export -f getent
    username=guest; groups='998:wheel 999: 1001:bad.name 1002:wheel'
    export username groups
    bash "$fixture/group-init"
    bash "$fixture/group-init"
    grep -qx 'systemd-journal:x:998:journaluser,guest' "$fixture/groups/group"
    grep -qx 'hostgrp999:x:999:guest' "$fixture/groups/group"
    grep -qx 'hostgrp1001:x:1001:guest' "$fixture/groups/group"
    grep -qx 'hostgrp1002:x:1002:guest' "$fixture/groups/group"
    [ "$(cut -d: -f3 "$fixture/groups/group" | sort -u | wc -l)" = 5 ]
    [ "$(wc -l < "$fixture/groups/group")" = 5 ]
}
regression "init preserves gid membership and sanitizes missing or invalid names" groups_test

host_groups_test() {
    regression_setup
    untrusted=""
    getent() {
        if [ "$1" = group ]; then
            if [ "$2" = "$(id -g)" ]; then echo "bad group:x:$2:"; else return 2; fi
        else
            command getent "$@"
        fi
    }
    ensure_box hostgroups
    groups=$(sed -n '5p' "$ROOT/hostgroups/config/identity")
    for gid in $(id -G); do [[ "$groups" = *"$gid:hostgrp$gid "* ]]; done
}
regression "host identity sanitizes group names before tokenizing" host_groups_test

forward_test() {
    mkdir -p "$fixture/ssh-bin"
    printf '#!/bin/sh\nprintf "%%s\\n" "$@"\n' > "$fixture/ssh-bin/ssh"
    chmod +x "$fixture/ssh-bin/ssh"
    PATH="$fixture/ssh-bin:$PATH" ssh_box vm true > "$fixture/ssh-args"
}
forward_assert() {
    (forward_test)
    grep -qx ExitOnForwardFailure=yes "$fixture/ssh-args"
}
regression "failed reverse forwards must fail the session" forward_assert

build_dep_test() {
    regression_setup
    command() {
        if [ "${2:-}" = "$missing" ]; then return 1; fi
        builtin command "$@"
    }
    fake_docker() { touch "$fixture/unexpected-build"; return 43; }
    QEMUBOX_DOCKER=fake_docker
    for missing in fake_docker bsdtar mke2fs; do
        if build_base 2> "$fixture/deps-error"; then exit 1; fi
        [ ! -f "$fixture/unexpected-build" ]
        grep -q "Missing:.*$missing" "$fixture/deps-error"
    done
}
regression "missing build dependencies fail before Docker build or export" build_dep_test

mke2fs_test() {
    regression_setup
    fake_docker() { touch "$fixture/unexpected-mke-build"; return 43; }
    mke2fs() { echo 'tar input unsupported' >&2; return 1; }
    QEMUBOX_DOCKER=fake_docker
    if build_base 2> "$fixture/mke-error"; then exit 1; fi
    [ ! -f "$fixture/unexpected-mke-build" ]
    grep -q 'Missing: mke2fs with -d tarball support' "$fixture/mke-error"
}
regression "mke2fs tar input is probed before building" mke2fs_test

temp_test() {
    regression_setup
    mktemp() { echo "$*" > "$fixture/mktemp-args"; command mktemp "$@"; }
    fake_docker() { return 43; }
    QEMUBOX_DOCKER=fake_docker
    set +e
    (set -e; build_base)
    rc=$?
    set -e
    [ "$rc" = 43 ]
    [ "$(cat "$fixture/mktemp-args")" = -d ]
}
regression "build temporary directory follows mktemp default" temp_test
