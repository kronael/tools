reset_mounts() { mount_tags=(); mount_srcs=(); mount_dests=(); mount_modes=(); }
mount_mode() {
    local i
    for i in "${!mount_dests[@]}"; do
        [ "${mount_dests[$i]}" = "$1" ] && { printf '%s' "${mount_modes[$i]}"; return; }
    done
}
run_assemble() {
    reset_mounts
    name=testbox; primary="$PROJ"; dirs=("$PROJ")
    gcloud_creds=""; untrusted=""; extra_dirs=(); extra_modes=()
    eval "${1:-:}"
    assemble_mounts
}
slug_dest="$GUEST_HOME/.claude/projects/${PROJ//\//-}"
LIB="$fixture/lib"; mkdir -p "$LIB"

run_assemble
eq "default: project rw"         "$(mount_mode "$PROJ")" "rw"
for d in .claude .codex .agents; do
    eq "default: $d rw at host path" "$(mount_mode "$HOME/$d")" "rw"
done
eq "default: no per-slug mount" "$(mount_mode "$slug_dest")" ""
eq "default: single-file config ro" "$(mount_mode /mnt/qemubox-home)" "ro"
eq "default: shell history rw" "$(mount_mode /mnt/qemubox-history)" "rw"
true_ "history shares host inode" '[ "$HOME/.dockbox_history" -ef "$ROOT/testbox/history/history" ]'
echo history-test >> "$ROOT/testbox/history/history"
eq "history writes reach host" "$(cat "$HOME/.dockbox_history")" "history-test"
mount_args=$(qemu_mount_args)
for i in "${!mount_tags[@]}"; do
    true_ "qemu socket ${mount_dests[$i]}" \
        'grep -Fxq "socket,id=${mount_tags[$i]},path=${mount_tags[$i]}.sock" <<< "$mount_args"'
    true_ "qemu device ${mount_dests[$i]}" \
        'grep -Fxq "vhost-user-fs-pci,queue-size=1024,chardev=${mount_tags[$i]},tag=${mount_tags[$i]}" <<< "$mount_args"'
done
false_ "virtiofs exports use no -virtfs" 'grep -q -- -virtfs <<< "$mount_args"'

printf '{"fixture":true}\n' > "$HOME/.claude.json"
stage_host_cfg "$ROOT/testbox/hostcfg"
true_ "claude.json staged intact" 'cmp "$HOME/.claude.json" "$ROOT/testbox/hostcfg/.claude.json"'
false_ "history excluded from ro staging" '[ -e "$ROOT/testbox/hostcfg/.dockbox_history" ]'
run_assemble
true_ "history staging supports re-entry" '[ "$HOME/.dockbox_history" -ef "$ROOT/testbox/history/history" ]'

run_assemble 'untrusted=1'
eq   "untrusted: project still rw"     "$(mount_mode "$PROJ")" "rw"
eq   "untrusted: no .claude cfg mount" "$(mount_mode "$HOME/.claude")" ""
eq   "untrusted: no qemubox-home"      "$(mount_mode /mnt/qemubox-home)" ""
eq   "untrusted: no per-slug memory"   "$(mount_mode "$slug_dest")" ""
eq   "untrusted: no history"          "$(mount_mode /mnt/qemubox-history)" ""

run_assemble 'dirs=()'
eq "-T: project not mounted" "$(mount_mode "$PROJ")" ""

run_assemble 'extra_dirs=("'"$LIB"'"); extra_modes=(ro)'
eq "extra -v mount honors ro mode" "$(mount_mode "$LIB")" "ro"

mkdir -p "$PROJ/node_modules/hidden/.cache" "$PROJ/.next" \
    "$PROJ/packages/a/.turbo" "$PROJ/packages/b/.cache" \
    "$PROJ/a/b/c/node_modules" "$PROJ/a/b/c/d/node_modules" \
    "$PROJ/space dir/node_modules" "$PROJ/server/.venv" "$PROJ/build"
dirs=("$PROJ"); persist_builds=""; eph_no_tmpfs=""
eph="$fixture/ephemeral"
stage_ephemeral "$eph"
mapfile -d '' -t paths < "$eph"
eq "default build mode" "${paths[0]}" tmpfs
eq "find prunes matches and caps depth" "${#paths[@]}" 8
for path in node_modules .next packages/a/.turbo packages/b/.cache \
    a/b/c/node_modules 'space dir/node_modules' server/.venv; do
    true_ "ephemeral: $path" 'printf "%s\n" "${paths[@]}" | grep -Fxq "$PROJ/$path"'
done

apply_flag P; stage_ephemeral "$eph"
mapfile -d '' -t paths < "$eph"
eq "-P disables project overmounts" "${#paths[@]}" 1
persist_builds=""; apply_flag B; stage_ephemeral "$eph"
mapfile -d '' -t paths < "$eph"
eq "-B chooses guest disk" "${paths[0]}" disk
eq "-B keeps same build dirs" "${#paths[@]}" 8
dirs=(); stage_ephemeral "$eph"
mapfile -d '' -t paths < "$eph"
eq "-T stages no project overmount" "${#paths[@]}" 1
dirs=("$PROJ"); eph_no_tmpfs=""
exits 1 'set -e; dirs=("$fixture/missing"); stage_ephemeral "$eph"' "failed find stops launch"

(
    ssh_stream_box() { cat > "$fixture/guest-builds.sh"; }
    setup_guest_builds testbox
)
(
    set -e
    mount() { printf '%s\n' "$*" >> "$fixture/mounts"; }
    mkdir() { :; }
    chown() { printf '%s\n' "$*" >> "$fixture/chown"; }
    export -f mount mkdir chown
    export fixture
    printf '%s\0' tmpfs "$PROJ/space dir/node_modules" > "$eph"
    bash "$fixture/guest-builds.sh" 1234 5678 "$eph"
    key=$(realpath -e "$PROJ/space dir/node_modules" | sha256sum); key=${key%% *}
    grep -Fx -- "--bind /tmp/qemubox-builds/$key $PROJ/space dir/node_modules" "$fixture/mounts"
    grep -Fx -- "1234:5678 /tmp/qemubox-builds/$key" "$fixture/chown"
    ! grep -q -- "-t tmpfs" "$fixture/mounts"
    printf '%s\0' disk "$PROJ/node_modules" > "$eph"
    bash "$fixture/guest-builds.sh" 1234 5678 "$eph"
    key=$(realpath -e "$PROJ/node_modules" | sha256sum); key=${key%% *}
    grep -Fx -- "--bind /var/lib/qemubox/builds/$key $PROJ/node_modules" "$fixture/mounts"
    grep -Fx -- "1234:5678 /var/lib/qemubox/builds/$key" "$fixture/chown"
    mount() { echo "mount denied" >&2; return 32; }
    export -f mount
    for mode in tmpfs disk; do
        printf '%s\0' "$mode" "$PROJ/node_modules" > "$eph"
        if bash "$fixture/guest-builds.sh" 1234 5678 "$eph"; then exit 1; else
            [ "$?" -eq 32 ]
        fi
    done
) > "$fixture/build-tests.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/build-tests.log"; bad "guest build mounts and failures"; }

(
    set -e
    ssh_stream_box() { bash -c "$2"; }
    sudo() { "$@"; }
    mount() { echo "$*" >> "$fixture/tmp-mounts"; }
    install() { echo "$*" >> "$fixture/tmp-installs"; }
    export fixture
    export -f sudo mount install
    setup_guest_tmp testbox
    grep -Fx -- '-t tmpfs -o rw,exec,mode=1777,size=75% tmpfs /tmp' "$fixture/tmp-mounts"
    grep -Fx -- "-d -o $(id -u) -g $(id -g) /tmp/cargo-target" "$fixture/tmp-installs"
    [ "$(wc -l < "$fixture/tmp-mounts")" = 1 ]
) > "$fixture/tmp-tests.log" 2>&1
[ "$?" -eq 0 ] && ok || { cat "$fixture/tmp-tests.log"; bad "guest tmp cap and cargo-target dir"; }

exits 32 'set -e; ssh_stream_box() { return 32; }; setup_guest_tmp testbox' \
    "failed tmp mount stops launch"
exits 32 'set -e; ssh_plain_box() { case "$2" in *"sudo mount"*) return 32;; esac; }; mount_host_paths testbox' \
    "failed virtiofs mount stops launch"
tab_dir="$fixture/tab"$'\t'"dir"
mkdir -p "$tab_dir"
exits 2 'add_mount "$tab_dir" /x rw' "a tab in a share path is refused"
exits 2 'add_mount "$PROJ" "$tab_dir" rw' \
    "a tab in a share destination is refused"
newline_dir="$fixture/newline"$'\n'"dir"
mkdir -p "$newline_dir"
exits 2 'add_mount "$newline_dir" /x rw' \
    "a newline in a share source is refused"
exits 2 'add_mount "$PROJ" "$newline_dir" rw' \
    "a newline in a share destination is refused"
comma_dir="$fixture/comma,dir"
mkdir -p "$comma_dir"
true_ "commas in share paths are accepted" \
    'reset_mounts; add_mount "$comma_dir" /comma,dest ro; [ "${mount_srcs[0]}" = "$comma_dir" ] && [ "${mount_dests[0]}" = /comma,dest ]'

guest_virtiofs_test() {
    reset_mounts
    add_mount "$PROJ" /readonly ro
    add_mount "$PROJ" /writable rw
    add_mount "$PROJ" /run/qemubox/config ro required cfg
    setup_mount_path() { :; }
    ssh_plain_box() { printf '%s\n' "$2" >> "$fixture/virtiofs-guest"; }
    mount_host_paths vm
    grep -Fxq 'mountpoint -q /readonly || sudo mount -t virtiofs -o ro qbx0 /readonly' \
        "$fixture/virtiofs-guest"
    grep -Fxq 'mountpoint -q /writable || sudo mount -t virtiofs -o rw qbx1 /writable' \
        "$fixture/virtiofs-guest"
    ! grep -q '/run/qemubox/config' "$fixture/virtiofs-guest"
}
regression "guest mounts virtiofs with each mode and keeps the boot config mount" \
    guest_virtiofs_test

canonical_newline_test() {
    untrusted=1
    dirs=()
    extra_modes=(ro)
    mkdir -p "$fixture/target" "$fixture/target"$'\n'
    ln -s "$fixture/target"$'\n' "$fixture/volume-link"
    extra_dirs=("$fixture/volume-link")
    if (assemble_mounts) 2> "$fixture/canonical-error"
    then
        return 1
    else
        [ "$?" = 2 ]
    fi
    grep -q 'containing tab or newline' "$fixture/canonical-error"
}
regression "a canonical share path keeps its trailing newline and refuses the prefix path" \
    canonical_newline_test
