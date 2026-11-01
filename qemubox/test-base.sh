base_fixture() {
    regression_setup
    source_dir="$fixture/base-source-$BASHPID"
    mkdir -p "$source_dir/qemubox" "$fixture/export-rootfs/bin"
    cp "$here/"{Dockerfile.kernel,kernel.fragment,initrd-init,Dockerfile} \
        "$source_dir/qemubox/"
    printf 'setuid fixture\n' > "$fixture/export-rootfs/bin/sudo"
    chmod 4755 "$fixture/export-rootfs/bin/sudo"
    touch "$fixture/export-rootfs/.dockerenv"
    QEMUBOX_SOURCE="$source_dir"
    QEMUBOX_DOCKER=fake_docker
    docker_log="$fixture/docker-$BASHPID"
    removed_log="$fixture/removed-$BASHPID"
    export_rc=0
    fake_docker() {
        printf '%s\n' "$*" >> "$docker_log"
        case "$1" in
            build) ;;
            image)
                if [[ "$4" = '{{.Id}}' ]]
                then
                    printf 'sha256:%064d\n' 7
                else
                    echo 107374182400
                fi ;;
            run) printf '1048576\t/\n' ;;
            create) echo fixture-container ;;
            cp) echo kernel > "$3" ;;
            export)
                command tar -cp -C "$fixture/export-rootfs" .
                return "$export_rc" ;;
            rm) echo "$2" >> "$removed_log" ;;
            *) return 98 ;;
        esac
    }
}

base_export_test() {
    base_fixture
    df() { printf 'Avail\n2147483648\n'; }
    local image_id kernel_id log lines changed
    printf -v image_id '%064d' 7
    build_base
    [[ "$(cat "$ROOT/base/current")" = "$image_id" ]]
    kernel_id=$(cat "$ROOT/base/kernel/current")
    [[ "$kernel_id" =~ ^[a-f0-9]{64}$ ]]
    for file in bzImage initrd kernel.config
    do
        [[ -s "$ROOT/base/kernel/$kernel_id/$file" ]]
    done
    [[ -f "$ROOT/base/$image_id/exported" ]]
    [[ ! -e "$ROOT/base/$image_id/rootfs/.dockerenv" ]]
    [[ "$(stat -c %a "$ROOT/base/$image_id/rootfs/bin/sudo")" = 4755 ]]
    [[ "$(stat -c %u "$ROOT/base/$image_id/rootfs/bin/sudo")" = "$(id -u)" ]]
    log=$(cat "$docker_log")
    [[ "$log" == *"create qemubox-kernel:$kernel_id /unused"* ]]
    [[ "$log" == *"export fixture-container"* ]]
    [[ "$log" != *'export -o'* ]]
    lines=$(wc -l < "$docker_log")
    build_base
    [[ "$(wc -l < "$docker_log")" = "$((lines + 2))" ]]
    for file in Dockerfile.kernel kernel.fragment initrd-init
    do
        printf '\n' >> "$source_dir/qemubox/$file"
        build_base
        changed=$(cat "$ROOT/base/kernel/current")
        [[ "$changed" != "$kernel_id" ]]
        [[ -s "$ROOT/base/kernel/$changed/bzImage" ]]
        grep -q -- "-t qemubox-kernel:$changed " "$docker_log"
        kernel_id=$changed
    done
}
regression 'base export preserves modes and owners; complete builds reuse artifacts' \
    base_export_test

base_failure_test() {
    base_fixture
    local image_id
    printf -v image_id '%064d' 7
    export_rc=42
    if build_base > "$fixture/export-output" 2>&1
    then
        return 1
    else
        [[ "$?" = 42 ]]
    fi
    [[ "$(cat "$ROOT/base/current")" = fixture ]]
    [[ "$(cat "$ROOT/base/kernel/current")" = fixture ]]
    [[ ! -e "$ROOT/base/$image_id/exported" ]]
    [[ -s "$ROOT/base/$image_id/rootfs/bin/sudo" ]]
    [[ "$(tail -1 "$removed_log")" = fixture-container ]]
    export_rc=0
    build_base
    [[ "$(cat "$ROOT/base/current")" = "$image_id" ]]
}
regression 'a failed streamed export stays visible and cannot publish a base' \
    base_failure_test

base_publish_failure_test() {
    local stage
    for stage in marker-write marker-rename kernel-write kernel-rename \
        current-write current-rename
    do
        (
            base_fixture
            printf -v image_id '%064d' 7
            case "$stage" in
                marker-*) target="$ROOT/base/$image_id/exported" ;;
                kernel-*) target="$ROOT/base/kernel/current" ;;
                current-*) target="$ROOT/base/current" ;;
            esac
            if [[ "$stage" = *-write ]]
            then
                mkdir -p "$target.tmp"
            else
                mv() {
                    [[ "${!#}" != "$target" ]] || return 44
                    command mv "$@"
                }
            fi
            if build_base > "$fixture/publish-$stage.log" 2>&1
            then
                return 1
            fi
            [[ "$(cat "$ROOT/base/current")" = fixture ]]
            ! grep -q 'base ready:' "$fixture/publish-$stage.log"
            if [[ "$stage" = marker-* ]]
            then
                [[ ! -s "$target" ]]
            fi
        )
    done
}
regression 'conditional callers cannot publish after marker or pointer failures' \
    base_publish_failure_test

base_space_test() {
    base_fixture
    df() { printf 'Avail\n0\n'; }
    if build_base > "$fixture/space-output" 2>&1
    then
        return 1
    fi
    [[ "$(cat "$ROOT/base/current")" = fixture ]]
    grep -q 'Insufficient base space:' "$fixture/space-output"
    ! grep -q '^export ' "$docker_log"
}
regression 'insufficient rootfs space refuses export without publishing' base_space_test

legacy_disk_test() {
    regression_setup
    mkdir -p "$ROOT/legacy"
    echo disk > "$ROOT/legacy/disk.qcow2"
    truncate() { touch "$fixture/legacy-opened"; return 1; }
    if ensure_box legacy 2> "$fixture/legacy-error"
    then
        return 1
    fi
    [[ ! -e "$fixture/legacy-opened" && ! -e "$ROOT/legacy/upper.raw" ]]
    grep -q 'qemubox rm legacy.*launch again' "$fixture/legacy-error"
    unset -f truncate
    ensure_box pinned
    echo another > "$ROOT/base/current"
    ensure_box pinned
    [[ "$(cat "$ROOT/pinned/image-id")" = fixture ]]
}
regression 'qcow2 is refused before raw open and current changes preserve image pins' \
    legacy_disk_test

format_failure_test() {
    regression_setup
    mkfs.ext4() { return 32; }
    if ensure_box broken
    then
        return 1
    else
        [[ "$?" = 32 ]]
    fi
    [[ ! -e "$ROOT/broken/upper.raw" && ! -e "$ROOT/broken/image-id" ]]
    [[ ! -e "$ROOT/broken/trust" ]]
    remove_box broken
    [[ ! -e "$ROOT/broken" ]]
}
regression 'failed formatting cannot publish an upper or disk identity' \
    format_failure_test

missing_base_test() {
    regression_setup
    untrusted=1
    ensure_box pinned
    echo retained > "$ROOT/pinned/upper.raw"
    rm "$ROOT/base/fixture/exported"
    if (ensure_box pinned) 2> "$fixture/missing-base-error"
    then
        return 1
    fi
    grep -q 'Missing base file.*qemubox rm pinned' "$fixture/missing-base-error"
    [[ "$(cat "$ROOT/pinned/upper.raw")" = retained ]]
}
regression 'missing recorded base refuses launch and preserves the upper' missing_base_test
