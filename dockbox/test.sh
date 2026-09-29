#!/usr/bin/env bash
# Tests for dockbox without a docker daemon. Sources the script with
# DOCKBOX_LIB=1 so the CLI never runs and no container is created; asserts the
# rm matcher, the tmpfs_used total, the -n name guard shared with qemubox and
# the -K flag, then runs `dockbox ls` against a stub docker on PATH.
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

## rm_matches (bare or dockbox- prefixed) -----------------------------------
false_ "rm empty pattern matches nothing"  'rm_matches dockbox-repo ""'
true_  "rm '\''*'\'' matches all"               'rm_matches dockbox-repo "*"'
true_  "rm exact bare"                     'rm_matches dockbox-repo repo'
true_  "rm exact full name"                'rm_matches dockbox-repo dockbox-repo'
false_ "rm exact no substring"             'rm_matches dockbox-repo-facade repo'
true_  "rm glob star"                      'rm_matches dockbox-repo-1 "repo-*"'
false_ "rm glob non-match"                 'rm_matches dockbox-other "repo-*"'

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

## ls against a stub docker on PATH ----------------------------------------
tmp=$(mktemp -d)
trap 'rm -rf -- "$tmp"' EXIT
cat > "$tmp/docker" <<'STUB'
#!/bin/bash
case "$1" in
    container)
        printf '%s\t%s\t%s\t%s\t%s\n' \
            dockbox-up running "Up 2 hours" "2 hours ago" "12.3MB (virtual 1.2GB)" \
            dockbox-old exited "Exited (0) 3 days ago" "5 days ago" "0B (virtual 1.2GB)" \
            dockbox-bad running "Up 1 minute" "1 minute ago" "1kB (virtual 1.2GB)" ;;
    exec)
        [ "$2" = dockbox-bad ] && { echo "Error: exec failed" >&2; exit 1; }
        cat <<'EOF'
Type    Used Mounted on
tmpfs     84 /tmp
tmpfs  20480 /tmp/cargo-target
tmpfs      0 /dev/shm
tmpfs 102400 /home/dockbox
tmpfs 102500 /home/dockbox
EOF
        ;;
esac
STUB
chmod +x "$tmp/docker"
ls_out=$(PATH="$tmp:$PATH" bash "$here/dockbox" ls 2>/dev/null)
true_  "ls totals a running box's tmpfs" 'grep -Eq "^dockbox-up .* 120M +12.3MB$" <<< "$ls_out"'
true_  "ls shows - for an exited box"    'grep -Eq "^dockbox-old .* - +0B$" <<< "$ls_out"'
true_  "ls shows ? when exec fails"      'grep -Eq "^dockbox-bad .* [?] +1kB$" <<< "$ls_out"'
false_ "ls strips the DISK virtual size" 'grep -q virtual <<< "$ls_out"'

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
