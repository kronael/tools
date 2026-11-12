# Diff gates

Two checks over the range step 3 resolved. Both run on every change, whatever
its size, at step 3 and again after the fixes at step 10. A hit is a finding
fixed at step 8: NEVER recorded for later, NEVER settled by an explanation.

## Module-relative paths

ALWAYS list the added lines that locate a path from the module, the script or
the binary:

```sh
git diff -U0 <base>...<head> | awk '
  BEGIN {
    shape = "__file__|[.]parents *[[]|__dirname|__filename|import[.]meta[.](url|dirname|filename)"
    shape = shape "|(basename|dirname|realpath|readlink)[^|;]*[$][{]?0|BASH_SOURCE"
    shape = shape "|current_exe|os[.]Executable"
  }
  /^\+\+\+ / { file = substr($0, 7); next }
  /^@@/ { line = substr($3, 2) + 0; next }
  /^\+/ { if ($0 ~ shape) print file ":" line ": " substr($0, 2); line++ }'
```

- Every printed line that builds a path from where the module, the script or
  the binary sits breaks `software/code.md` § Layout and formatting. ALWAYS fix
  it the way that section states; NEVER keep one with a reason beside it. A
  line that only names the shape — prose, a lint pattern — builds no path.
- ALWAYS trace a `parents[N]` hit to its anchor: bound from `__file__`, on an
  unchanged line included, it is the same defect; bound from configuration, it
  is none.
- The one exception is the one that section allows: an installed tool reading
  its own shipped read-only resources. ALWAYS name each kept line in the
  closing report with the resource it reads. A test fixture, a repo root, an
  output or a state path is NEVER that resource.

## Test edits follow the interface

```sh
python3 ~/.claude/skills/refine/assertions.py <base> <head>
```

`assertions.py` sits beside this file. It reads the changed Python files named
`test_*.py`, `*_test.py` or `conftest.py`, or under a `tests/` or `test/`
directory, and compares each function's checks before and after: `assert`,
`raises`/`warns`, `assert*` calls and `parametrize`. Functions pair through git
renames, then by name across files. It prints candidates to classify:

- a function that lost or changed a check: `-` before, `+` after;
- a removed test, and a removed helper that held a check; a test left in a file
  named neither `test_*.py` nor `*_test.py` counts as removed;
- a `pytest` or `unittest` skip or xfail the range added or changed on a
  function that existed before, on its class or on its module: `+ disabled by`.

Exit 0: none; 1: lines to classify; 2: failed check. Its last line counts the
functions compared; `0 of 0` compared nothing. It compares source text: it
resolves no alias, follows no control flow and reads no pytest configuration.

- ALWAYS classify every `-` line as exactly one of three: the same check
  through an updated call or argument, its `+` line asserting the same fact; a
  case the new types make impossible, the type named; a deliberate contract
  change that the change's description names. Anything else is a weakened
  test: ALWAYS restore it.
- ALWAYS list every removed test function by name in the description — the PR
  body, or the commit body when no PR exists — with its reason. A test that a
  `+ disabled by` line newly skips is a removed test.
- ALWAYS quote the script's last line in the closing report. Exit 2 is NEVER a
  clean result; on a `SyntaxError`, ALWAYS rerun under the project's
  interpreter (`uv run python …`) before reading the source as broken.
- For tests the script does not read — another language, a file outside those
  names — ALWAYS make the same comparison by hand over `git diff -M
  <base>...<head> -- <test paths>`: every removed line holding an assertion or
  an expected error is classified the same way.
- The script compares what tests state. Whether a check runs, or exercises
  production code, is `software.md` § Tests that prove nothing.
