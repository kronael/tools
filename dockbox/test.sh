#!/usr/bin/env bash
# Tests for dockbox without a docker daemon. Sources the script with
# DOCKBOX_LIB=1 so the CLI never runs and no container is created; asserts the
# rm matcher, the tmpfs_used total, the box_use classifier, the -n name guard
# shared with qemubox and the -K flag, then runs ls, prune, rm and a session
# against a stub docker on PATH.
set -uo pipefail

here="$(cd "$(dirname "$0")" && pwd)"

# shellcheck disable=SC1090
DOCKBOX_LIB=1 . "$here/dockbox"
set +e  # sourcing turned on set -e; take back control for assertions

pass=0; fail=0
ok()   { pass=$((pass+1)); }
bad()  { fail=$((fail+1)); echo "FAIL: $1" >&2; }
true_() { if eval "$2"; then ok; else bad "$1"; fi; }
false_(){ if eval "$2"; then bad "$1"; else ok; fi; }
exits() { ( eval "$2" ) >/dev/null 2>&1; [ "$?" = "$1" ] && ok || bad "$3"; }

tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT

## rm_matches (bare or dockbox- prefixed) -----------------------------------
false_ "rm empty pattern matches nothing"  'rm_matches dockbox-repo ""'
true_  "rm '\''*'\'' matches all"               'rm_matches dockbox-repo "*"'
true_  "rm exact bare"                     'rm_matches dockbox-repo repo'
true_  "rm exact full name"                'rm_matches dockbox-repo dockbox-repo'
false_ "rm exact no substring"             'rm_matches dockbox-repo-facade repo'
true_  "rm glob star"                      'rm_matches dockbox-repo-1 "repo-*"'
false_ "rm glob non-match"                 'rm_matches dockbox-other "repo-*"'
false_ "rm prefixed name is taken literally" 'rm_matches dockbox-dockbox-repo dockbox-repo'

## tmpfs_used (ls TMPFS column) --------------------------------------------
df_out='Type    Used Mounted on
tmpfs     84 /tmp
ext4  900000 /tmp/cargo-target
tmpfs 109604 /home/dockbox
tmpfs 109604 /home/dockbox'
true_ "tmpfs sums each mount once, skips non-tmpfs" \
    '[ "$(tmpfs_used <<< "$df_out")" = 107M ]'
true_ "tmpfs prints G from 1G up" \
    '[ "$(printf "h\ntmpfs 3145728 /tmp\n" | tmpfs_used)" = 3.0G ]'
true_ "tmpfs empty is 0M" '[ "$(printf "h\n" | tmpfs_used)" = 0M ]'
true_ "tmpfs counts a mount sampled twice at new usage once" \
    '[ "$(printf "h\ntmpfs 4096 /home/dockbox\ntmpfs 5120 /home/dockbox\n" | tmpfs_used)" = 4M ]'
true_ "tmpfs keys the whole target, spaces included" \
    '[ "$(printf "h\ntmpfs 1024 /w/a b\ntmpfs 2048 /w/a c\n" | tmpfs_used)" = 3M ]'

## box_use (ls USE column, prune eligibility) -----------------------------
cat > "$tmp/top-idle" <<'EOF'
UID          PID    PPID  C STIME TTY          TIME CMD
root        4101    4080  0 09:00 ?        00:00:00 /sbin/docker-init -- /usr/local/bin/dockbox-init sleep infinity
1000        4150    4101  0 09:00 ?        00:00:00 sleep infinity
EOF
{ cat "$tmp/top-idle"
  echo "1000        4200    4180  3 Sep28 pts/0    00:01:02 claude --model claude-opus-5-5"
} > "$tmp/top-busy"
true_  "use idle when only the keepers run"   '[ "$(box_use < "$tmp/top-idle")" = idle ]'
true_  "use busy with any other process"      '[ "$(box_use < "$tmp/top-busy")" = busy ]'
false_ "use fails when top lists no process"  'head -1 "$tmp/top-idle" | box_use'

## commands against a stub docker on PATH ----------------------------------
# The stub serves the boxes in $STUB/boxes (name, state, age in seconds, use,
# size) through each --format template, answers `top` from the fixtures above,
# runs the session-marker snippets against $STUB/run and the ls probe against
# the fake box in $STUB/box — under dash when installed, the box's /bin/sh —
# and logs every call.
export STUB="$tmp"
log="$tmp/log"
cat > "$tmp/docker" <<'STUB'
#!/bin/bash
echo "$*" >> "$STUB/log"
box_sh=$(command -v dash || command -v sh)
use_of() { awk -F'\t' -v n="$1" '$1 == n { print $4 }' "$STUB/boxes"; }
case "$1" in
    container)
        while [ $# -gt 0 ] && [ "$1" != --format ]; do shift; done
        fmt="${2//\\t/$'\t'}"
        now=$(date +%s)
        while IFS=$'\t' read -r name state age use size; do
            created=$(date -d "@$((now - age))" "+%Y-%m-%d %H:%M:%S %z %Z" 2>/dev/null) ||
                created=$(date -r "$((now - age))" "+%Y-%m-%d %H:%M:%S %z %Z")
            status="Up $age seconds"
            [ "$state" = exited ] && status="Exited (0) $age seconds ago"
            row="${fmt//'{{.Names}}'/$name}"
            row="${row//'{{.State}}'/$state}"
            row="${row//'{{.Status}}'/$status}"
            row="${row//'{{.RunningFor}}'/$age seconds ago}"
            row="${row//'{{.Size}}'/$size}"
            echo "${row//'{{.CreatedAt}}'/$created}"
        done < "$STUB/boxes" ;;
    top)
        cat "$STUB/top-$(use_of "$2")" 2>/dev/null || { echo "Error: top failed" >&2; exit 1; } ;;
    exec)
        case "$*" in
            *" -it "*)
                [ -n "${STUB_WIPE:-}" ] && rm -f "$STUB"/run/sess/* && rmdir "$STUB/run/sess"
                exit "${STUB_RC:-0}" ;;
            */run/dockbox/sess*)
                script="${*: -1}"
                exec "$box_sh" -c "${script//"/run/dockbox"/$STUB/run}" ;;
            *"df -k"*)
                [ "$(use_of "$2")" = fail ] && { echo "Error: exec failed" >&2; exit 1; }
                script="${*: -1}"
                PATH="$STUB/box/bin:$PATH" exec "$box_sh" -c "${script//" /"/" $STUB/box/"}" ;;
        esac ;;
    ps) echo c0ffee ;;
    rm) [ "$(use_of "${*: -1}")" = fail ] && { echo "Error: rm failed" >&2; exit 1; } ;;
esac
exit 0
STUB
chmod +x "$tmp/docker"
# The fake box's df reports each path whose dir holds a .df (`fstype used`) and
# fails on any other, with df's own error for a missing one.
mkdir -p "$tmp/box/bin" "$tmp/box/tmp/cargo-target" "$tmp/box/dev/shm" \
    "$tmp/box/home/dockbox" "$tmp/box/w/node_modules" "$tmp/box/w/broken"
echo "tmpfs 84"     > "$tmp/box/tmp/.df"
echo "tmpfs 20480"  > "$tmp/box/tmp/cargo-target/.df"
echo "tmpfs 0"      > "$tmp/box/dev/shm/.df"
echo "tmpfs 102400" > "$tmp/box/home/dockbox/.df"
echo "tmpfs 30720"  > "$tmp/box/w/node_modules/.df"
cat > "$tmp/box/bin/df" <<'DF'
#!/bin/sh
shift 2
echo "Type Used Mounted on"
rc=0
for p; do
    if [ -f "$p/.df" ]; then
        echo "$(cat "$p/.df") $p"
    elif [ -e "$p" ]; then
        echo "df: $p: Input/output error" >&2; rc=1
    else
        echo "df: $p: No such file or directory" >&2; rc=1
    fi
done
exit "$rc"
DF
chmod +x "$tmp/box/bin/df"
boxes() { printf '%s\t%s\t%s\t%s\t%s\n' "$@" > "$tmp/boxes"; }
dockbox() { : > "$log"; PATH="$tmp:$PATH" bash "$here/dockbox" "$@"; }

## ls ------------------------------------------------------------------------
boxes dockbox-up   running 7200   idle "12.3MB (virtual 1.2GB)" \
      dockbox-busy running 7200   busy "5MB (virtual 1.2GB)" \
      dockbox-old  exited  432000 -    "0B (virtual 1.2GB)" \
      dockbox-bad  running 60     fail "1kB (virtual 1.2GB)"
ls_out=$(DOCKBOX_EPH_PATHS="$tmp/box/home/dockbox" dockbox ls 2>/dev/null)
true_  "ls header carries USE"           'grep -Eq "^NAMES +STATUS +CREATED +USE +TMPFS +DISK$" <<< "$ls_out"'
true_  "ls totals a running box's tmpfs" 'grep -Eq "^dockbox-up .* 120M +12.3MB$" <<< "$ls_out"'
true_  "ls shows - for an exited box"    'grep -Eq "^dockbox-old .* - +- +0B$" <<< "$ls_out"'
true_  "ls shows ? when the probes fail" 'grep -Eq "^dockbox-bad .* [?] +[?] +1kB$" <<< "$ls_out"'
true_  "ls USE idle with only keepers"   'grep -Eq "^dockbox-up .* idle +120M" <<< "$ls_out"'
true_  "ls USE busy with a session"      'grep -Eq "^dockbox-busy .* busy +120M" <<< "$ls_out"'
false_ "ls strips the DISK virtual size" 'grep -q virtual <<< "$ls_out"'
boxes dockbox-up running 60 idle 0B
ls_out=$(DOCKBOX_EPH_PATHS="$tmp/box/home/dockbox:$tmp/box/w/gone:$tmp/box/w/node_modules" \
    dockbox ls 2>"$tmp/err")
true_  "ls totals the mounts left past a vanished path" 'grep -Eq "^dockbox-up .* 150M +0B$" <<< "$ls_out"'
true_  "ls prints nothing for a vanished path"          '[ ! -s "$tmp/err" ]'
ls_out=$(DOCKBOX_EPH_PATHS="$tmp/box/home/dockbox:$tmp/box/w/broken" \
    dockbox ls 2>"$tmp/err")
true_  "ls shows ? when df fails on a path that exists" 'grep -Eq "^dockbox-up .* [?] +0B$" <<< "$ls_out"'
true_  "ls passes that df error through"                'grep -q "w/broken: Input/output error" "$tmp/err"'

## prune ---------------------------------------------------------------------
boxes dockbox-idle-old running 14410           idle 0B \
      dockbox-idle-new running 14399           idle 0B \
      dockbox-busy     running 18000           busy 0B \
      dockbox-bad      running 18000           fail 0B \
      dockbox-gone     exited  $((2161 * 3600)) -   0B \
      dockbox-recent   exited  3600            -    0B
prune_out=$(dockbox prune 2>/dev/null); rc=$?
true_  "prune exits 0 when every removal worked"   '[ "$rc" = 0 ]'
true_  "prune removes an idle box past the grace"  'grep -qx "rm -f -v dockbox-idle-old" "$log"'
false_ "prune spares an idle box inside the grace" 'grep -q "^rm .*dockbox-idle-new$" "$log"'
false_ "prune spares a busy box"                   'grep -q "^rm .*dockbox-busy$" "$log"'
false_ "prune spares a box whose probe fails"      'grep -q "^rm .*dockbox-bad$" "$log"'
true_  "prune removes an exited box past [hours]"  'grep -qx "rm -f -v dockbox-gone" "$log"'
false_ "prune spares a young exited box"           'grep -q "^rm .*dockbox-recent$" "$log"'
true_  "prune prints what it removed" \
    '[ "$prune_out" = "$(printf "removed %s\n" dockbox-idle-old dockbox-gone)" ]'

## rm ------------------------------------------------------------------------
boxes dockbox-a            running 60 idle 0B \
      dockbox-b            exited  60 -    0B \
      dockbox-c            running 60 busy 0B \
      dockbox-repo         running 60 idle 0B \
      dockbox-dockbox-repo running 60 idle 0B
dockbox rm a b >/dev/null 2>&1; rc=$?
true_  "rm removes every name given" \
    '[ "$rc" = 0 ] && [ "$(grep "^rm " "$log")" = "$(printf "rm -f -v %s\n" dockbox-a dockbox-b)" ]'
dockbox rm dockbox-repo >/dev/null 2>&1
true_  "rm of a prefixed name removes only that box" \
    '[ "$(grep "^rm " "$log")" = "rm -f -v dockbox-repo" ]'
dockbox rm a -x >/dev/null 2>&1; rc=$?
true_  "rm rejects an unknown option, removing nothing" '[ "$rc" = 2 ] && ! grep -q "^rm " "$log"'
exits 1 'dockbox rm nope' "rm exits 1 when a pattern matches nothing"
dockbox rm -a >/dev/null 2>&1
true_  "rm -a removes every box" '[ "$(grep -c "^rm -f -v " "$log")" = 5 ]'
boxes dockbox-stuck running 60 fail 0B
exits 1 'dockbox rm stuck' "rm exits 1 when docker rm fails"

## session cleanup -----------------------------------------------------------
mkdir -p "$tmp/home"
cd "$tmp/home" || exit 1
HOME="$tmp/home" STUB_RC=3 dockbox -n sess exec false >/dev/null 2>&1; rc=$?
true_  "a failed session exits with its status"   '[ "$rc" = 3 ]'
true_  "a failed session still tears the box down" 'grep -qx "rm -f -v dockbox-sess" "$log"'
touch "$tmp/run/sess/4242"
HOME="$tmp/home" dockbox -n sess exec true >/dev/null 2>&1
false_ "a session leaves the box to a live sibling" 'grep -q "^rm " "$log"'
rm -f "$tmp/run/sess/4242"
HOME="$tmp/home" STUB_WIPE=1 dockbox -n sess exec true >/dev/null 2>&1
false_ "a session keeps the box when markers can't be listed" 'grep -q "^rm " "$log"'
cd "$here" || exit 1

## -n traversal guard ------------------------------------------------------
exits 2 'apply_flag n ..'  "-n .. rejected"
exits 2 'apply_flag n ""'  "-n empty rejected"
exits 2 'apply_flag n a/b' "-n with slash rejected"
true_   "-n keys the dir, prefix stays" 'apply_flag n goodname; [ "$dir_override" = goodname ]'

## -K gpg opt-in ------------------------------------------------------------
gpg_forward=""; apply_flag K
true_ "-K sets gpg_forward" '[ -n "$gpg_forward" ]'

echo "dockbox/test.sh: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
