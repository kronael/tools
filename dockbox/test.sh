#!/usr/bin/env bash
# Unit tests for dockbox's pure helpers. Sources the script with DOCKBOX_LIB=1
# so the CLI never runs and no container is created; asserts the rm matcher and
# the -n name guard shared with qemubox.
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
