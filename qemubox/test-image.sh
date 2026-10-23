image_init="$here/guest-init"

codex_wrapper_test() {
    awk '/^    && printf.*#!\/bin\/sh/ && !/poweroff/ {
            emit=1;sub(/^    && /, "")}
        emit {print}
        emit && / > \/usr\/local\/bin\/codex/ {exit}' "$here/Dockerfile" |
        sed 's|> /usr/local/bin/codex|> "$fixture/emitted-codex"|' \
        > "$fixture/extract-codex"
    source "$fixture/extract-codex"
    sed 's|/opt/dev-tools/bun/bin/codex|"$QEMUBOX_TEST_CODEX"|' \
        "$fixture/emitted-codex" > "$fixture/codex-wrapper"
    grep -Fq 'exec "$QEMUBOX_TEST_CODEX" ' "$fixture/codex-wrapper"
    cat > "$fixture/fake-codex" <<'EOF'
#!/bin/sh
printf '%s\0' "$CODEX_HOME" "$CODEX_SQLITE_HOME" "$@" > "$QEMUBOX_TEST_ARGS"
EOF
    chmod +x "$fixture/fake-codex"
    CODEX_HOME="$HOME/.codex" CODEX_SQLITE_HOME=/tmp/codex-sqlite \
        QEMUBOX_TEST_CODEX="$fixture/fake-codex" \
        QEMUBOX_TEST_ARGS="$fixture/codex-args" \
        sh "$fixture/codex-wrapper" resume 'session with spaces' \
            -c 'model_reasoning_effort="xhigh"' '' 'literal $HOME $(false)'
    printf '%s\0' "$HOME/.codex" /tmp/codex-sqlite \
        --no-daemon --dangerously-bypass-approvals-and-sandbox \
        resume 'session with spaces' -c 'model_reasoning_effort="xhigh"' \
        '' 'literal $HOME $(false)' > "$fixture/want-codex-args"
    cmp "$fixture/want-codex-args" "$fixture/codex-args"
}
regression "guest Codex avoids the shared daemon and preserves user arguments" \
    codex_wrapper_test

sshd_test() {
    grep -q "'StreamLocalBindUnlink yes'" "$here/Dockerfile"
}
regression "guest sshd replaces stale Unix sockets" sshd_test

docker_cli_test() {
    sed '/^FROM dockbox AS vm/,$d' "$here/Dockerfile" | grep -qw docker-cli
}
regression "both images install docker-cli" docker_cli_test

timezone_test() {
    regression_setup
    untrusted=""
    ensure_box timezone
    [ "$(sed -n '6p' "$ROOT/timezone/config/identity")" = Etc/UTC ]
    mkdir -p "$fixture/zone/etc" "$fixture/zone/run/qemubox/config"
    cp "$ROOT/timezone/config/identity" \
        "$fixture/zone/run/qemubox/config/identity"
    awk '/^{/ {emit=1} emit {print}
        /^ln -sf .*zone.*localtime/ {exit}' "$image_init" |
        sed "s|/etc/|$fixture/zone/etc/|g; s|/run/|$fixture/zone/run/|g" \
        > "$fixture/zone-init"
    export fixture
    bash "$fixture/zone-init"
    [[ "$(readlink "$fixture/zone/etc/localtime")" = /usr/share/zoneinfo/Etc/UTC ]]
    if grep -q '^RUN for key in TZ ' "$here/Dockerfile"; then exit 1; fi
}
regression "identity and init set the UTC time zone" timezone_test

groups_test() {
    local prefix="$fixture/groups"
    mkdir -p "$prefix/etc"
    printf '%s\n' 'systemd-journal:x:998:journaluser' 'wheel:x:10:other' \
        'docker:x:997:dockeruser' > "$prefix/etc/group"
    printf '%s\n' 'systemd-journal:!::journaluser' 'wheel:!::other' \
        'docker:!::dockeruser' > "$prefix/etc/gshadow"
    printf '%s\n' 'root:x:0:0:root:/root:/bin/bash' > "$prefix/etc/passwd"
    printf '%s\n' 'root:!:19000:0:99999:7:::' > "$prefix/etc/shadow"
    printf '%s\n' 'PASS_MAX_DAYS 99999' 'PASS_MIN_DAYS 0' 'PASS_WARN_AGE 7' \
        > "$prefix/etc/login.defs"
    sed -n '/^groups=.*getent group docker/,/^echo .*ALL=(ALL)/p' \
        "$image_init" | sed '$d' > "$fixture/group-init"
    getent() {
        awk -F: -v key="$2" \
            '$1==key || $3==key {found=1;print} END {exit !found}' \
            "$prefix/etc/$1"
    }
    groupadd() { command groupadd -P "$prefix" "$@"; }
    useradd() { command useradd -P "$prefix" "$@"; }
    usermod() { command usermod -P "$prefix" "$@"; }
    export prefix
    export -f getent groupadd useradd usermod
    username=guest; user_uid=2001; user_gid=999; home_dir=/home/guest
    groups='998:wheel 999: 1001:bad.name 1002:wheel'
    export username user_uid user_gid home_dir groups
    bash -e "$fixture/group-init"
    bash -e "$fixture/group-init"
    grep -qx 'systemd-journal:x:998:journaluser,guest' "$prefix/etc/group"
    grep -qx 'hostgrp999:x:999:guest' "$prefix/etc/group"
    grep -qx 'hostgrp1001:x:1001:guest' "$prefix/etc/group"
    grep -qx 'hostgrp1002:x:1002:guest' "$prefix/etc/group"
    grep -qx 'docker:x:997:dockeruser,guest' "$prefix/etc/group"
    grep -qx 'guest:x:2001:999::/home/guest:/bin/bash' "$prefix/etc/passwd"
    grep -qxE 'guest:!:[0-9]+:0?:99999:7:::' "$prefix/etc/shadow"
    [ "$(cut -d: -f3 "$prefix/etc/group" | sort -u | wc -l)" = 6 ]
    [ "$(wc -l < "$prefix/etc/group")" = 6 ]
    printf '%s\n' 'root:!:19000:0:99999:7:::' > "$prefix/etc/shadow"
    bash -e "$fixture/group-init"
    grep -qxE 'guest:!:[0-9]+:0?:99999:7:::' "$prefix/etc/shadow"
    if user_uid=2002 bash -e "$fixture/group-init" 2> "$fixture/group-conflict"
    then
        return 1
    fi
    grep -q 'conflicting user guest' "$fixture/group-conflict"
    if home_dir=/other bash -e "$fixture/group-init"
    then
        return 1
    fi
}
regression "init preserves memberships and sanitizes group names" groups_test

host_groups_test() {
    regression_setup
    untrusted=""
    getent() {
        if [ "$1" = group ]; then
            if [[ "$2" = "$(id -g)" ]]
            then
                echo "bad group:x:$2:"
            else
                return 2
            fi
        else
            command getent "$@"
        fi
    }
    ensure_box hostgroups
    groups=$(sed -n '5p' "$ROOT/hostgroups/config/identity")
    for gid in $(id -G); do [[ "$groups" = *"$gid:hostgrp$gid "* ]]; done
}
regression "host identity sanitizes group names before tokenizing" \
    host_groups_test

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
    for missing in fake_docker tar sha256sum
    do
        if build_base 2> "$fixture/deps-error"; then exit 1; fi
        [ ! -f "$fixture/unexpected-build" ]
        grep -q "Missing:.*$missing" "$fixture/deps-error"
    done
}
regression "missing dependencies fail before Docker build or export" \
    build_dep_test

gnu_tar_test() {
    regression_setup
    fake_docker() { touch "$fixture/unexpected-tar-build"; return 43; }
    tar() { echo 'bsdtar'; }
    QEMUBOX_DOCKER=fake_docker
    if build_base 2> "$fixture/tar-error"; then exit 1; fi
    [ ! -f "$fixture/unexpected-tar-build" ]
    grep -q 'Missing: GNU tar' "$fixture/tar-error"
}
regression "build requires GNU tar before building" gnu_tar_test
