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

## -n traversal guard ------------------------------------------------------
exits 2 'apply_flag n ..'  "-n .. rejected"
exits 2 'apply_flag n ""'  "-n empty rejected"
exits 2 'apply_flag n a/b' "-n with slash rejected"
true_   "-n keys the dir, prefix stays" 'apply_flag n goodname; [ "$dir_override" = goodname ]'

## -K gpg opt-in ------------------------------------------------------------
gpg_forward=""; apply_flag K
true_ "-K sets gpg_forward" '[ -n "$gpg_forward" ]'

## sandbox note -------------------------------------------------------------
nout="$(sandbox_note myhost bridge \
    -v /h/.claude:/home/dockbox/.claude:rw -v /p:/p:rw \
    -v /tmp/s.json:/home/dockbox/.claude/settings.json:ro \
    -v /p/node_modules --tmpfs /home/dockbox:rw,exec,mode=1777)"
true_ "note names the sandbox"       '[[ "$nout" == *CLAUDE_SANDBOX=dockbox* ]]'
true_ "note names the host"          '[[ "$nout" == *"host \`myhost\`"* ]]'
true_ "note names the network"       '[[ "$nout" == *"Network: bridge"* ]]'
true_ "note maps a box path to host" '[[ "$nout" == *"- /home/dockbox/.claude (rw) <- /h/.claude"* ]]'
true_ "note marks a same-path mount" '[[ "$nout" == *"- /p (rw) <- same path"* ]]'
true_ "note keeps a ro mode"         '[[ "$nout" == *"settings.json (ro) <- /tmp/s.json"* ]]'
true_ "note lists volume and tmpfs as lost" \
    '[[ "$nout" == *"Lost at exit (tmpfs or volume): /p/node_modules /home/dockbox"* ]]'

echo "dockbox/test.sh: $pass passed, $fail failed"
[ "$fail" -eq 0 ]
