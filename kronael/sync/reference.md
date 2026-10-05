# Sync reference — scripts, keep-list, tool commands

Cold lookup data for `SKILL.md`. Read the section a step names when that step
runs; the decision logic stays in `SKILL.md`. Every script expects `SRC` (the
source root) and `RUN` (the run dir) exported and `$RUN/keep.py` written
(§ Keep-list), and writes nothing outside `RUN` unless its section says so.

## Keep-list (steps 0, 1, 3, 4)

`~/.claude/.keep` — one path per line, relative to `~/.claude/`, glob
patterns allowed (`*` stays inside one path segment); a line starting with `#`
is a comment. Each entry is an installed-only path inside one of the bundle
dirs that the owner wants back after every sync. A symlink under a bundle dir
— an org skill linked from its own checkout, a `ripwire-*` skill — is kept
without a line: it points at work that lives elsewhere, never at bundle
content.

```text
# installed-only paths a sync carries over; never published
skills/acme-deploy
agents/acme-oncall.md
```

A trailing `/` is dropped. An entry that is absolute, has an empty, `.` or
`..` segment, or names no path inside `skills/ agents/ hooks/ output-styles/
commands/` is an error: § Classify prints `BADKEEP <entry>` and exits 1, and
§ Swap refuses before it creates anything. An entry whose path the source
also has, as a file or a dir, shadows it: § Classify prints `shadow`, § Swap
refuses it, and the owner deletes the line.

Step 0 writes the one reader of the list; § Classify and § Swap both import
it, so the paths Classify prints as `kept` are the paths Swap copies:

```sh
cat > "$RUN/keep.py" <<'PY'
import glob, os, sys

DIRS = ('skills', 'agents', 'hooks', 'output-styles', 'commands')


def invalid(entry):
    parts = entry.split('/')
    return (os.path.isabs(entry) or parts[0] not in DIRS or len(parts) < 2
            or not {'', '.', '..'}.isdisjoint(parts))


def expand(live):
    """Paths under live that the keep-list names, plus every symlink under a
    bundle dir, outermost only.

    A bad entry prints BADKEEP lines and exits 1.
    """
    path = os.path.join(live, '.keep')
    try:
        lines = [x.strip() for x in open(path)] if os.path.isfile(path) else []
    except OSError as e:
        print(f'Cannot read {path}: {e.strerror}')
        sys.exit(1)
    entries = [x.rstrip('/') for x in lines if x and not x.startswith('#')]
    bad = [k for k in entries if invalid(k)]
    if bad:
        print('\n'.join(f'BADKEEP {k}' for k in bad))
        sys.exit(1)
    paths = {p for k in entries for p in glob.glob(k, root_dir=live)}
    for d in DIRS:
        if os.path.islink(os.path.join(live, d)):
            continue  # a symlinked bundle root: § Classify prints SYMLINK
        for root, dirs, names in os.walk(os.path.join(live, d)):
            paths |= {os.path.relpath(os.path.join(root, n), live)
                      for n in dirs + names if os.path.islink(os.path.join(root, n))}
    return sorted(p for p in paths
                  if not any(p.startswith(q + '/') for q in paths))


if __name__ == '__main__':
    expand(os.path.expanduser('~/.claude'))
PY
```

## Classify (step 1)

Read-only. Prints a count per class and one line per path that needs a
decision; exits 1 on a `BADKEEP`, `SYMLINK` or `UNRESOLVED` line. A live file
identical to any committed version of its source path is an older install,
not local work: it counts as `stale`. A `both` file whose three-way merge
into the repo copy changes nothing is `merged`. A path under a name the
bundle shipped and dropped (`RETIRED`), or a legacy nested
`skills/<name>/<name>/` copy, is `retired`: it moves aside with the old bundle
and needs no answer. Caches and the `.claude/` scratch a session run inside a
bundle dir leaves are `junk`. A bundle dir the live tree lacks (a first sync,
an older install) is skipped; a dir or file it cannot read, live or source,
stops the run with one `Cannot read <path>` line and exit 1. A symlink is
never read through: one under a bundle dir is `kept`, and a bundle root that
is one prints `SYMLINK <path>`. `UNRESOLVED` lines are
settings hook commands pointing at paths the swap would drop. Scratch files
go to `$RUN/classify/`. An empty or absent live bundle prints `no live bundle
files`.

```sh
PYTHONPATH="$RUN" python3 -B - <<'PY'
import hashlib, json, os, re, subprocess, sys
sys.path.insert(0, os.environ['RUN'])  # ahead of the CWD entry `python3 -` adds
import keep
src, home, tmp = os.environ['SRC'], os.path.expanduser('~'), os.path.join(os.environ['RUN'], 'classify')
live = os.path.join(home, '.claude')
JUNK = {'__pycache__', '.pytest_cache', '.ruff_cache', '.claude'}
WISDOM = 'skills/global/SKILL.md'
RETIRED = {  # names the bundle shipped and dropped: moved aside, never asked about
    *(f'skills/{n}' for n in (
        '13yo-eval', 'agent-browser', 'assess', 'bash', 'caveman', 'ceo-eval', 'codex', 'con',
        'cont', 'create-architecture-diagram', 'create-ascii-art', 'credits',
        'create-ascii-video', 'create-claude-design', 'create-code-presentation',
        'create-design-md', 'create-eval', 'create-excalidraw', 'create-humanizer',
        'create-manim-video', 'create-p5js', 'create-popular-web-designs', 'create-pretext',
        'create-sketch', 'create-video-render', 'create-video-script', 'cto-eval',
        'design-eval', 'doc-topology', 'docs-audit', 'eval-all', 'explore', 'eye-13yo',
        'finalize-crate',
        'gh-fix', 'gh-review', 'go-gl', 'hacker-eval', 'hiring-eval', 'later', 'markdown-converter',
        'media-ingest', 'merge-trivial', 'onepager', 'red-eval',
        'python', 'research-analysis', 'resolve', 'rust', 'settle', 'sol',
        'software-engineering', 'speed-demo', 'sub', 'testing', 'trader', 'typescript', 'useless',
    )),
    'hooks/context.py', 'hooks/extnudge.py', 'hooks/lib/toolchain.py', 'hooks/nudge.py',
    'hooks/redirect.py', 'output-styles/80-caveman.md',
}

def read(p):
    try:
        with open(p, 'rb') as f:
            return f.read()
    except OSError as err:
        sys.exit(f'Cannot read {p}: {err.strerror}')

def sha(b):
    return hashlib.sha256(b).hexdigest()

def body(b):  # wisdom body: after the second '---' line, leading blank lines dropped
    lines, n = b.splitlines(keepends=True), 0
    for i, line in enumerate(lines):
        n += line.rstrip(b'\r\n') == b'---'
        if n == 2:
            return b''.join(lines[i + 1:]).lstrip(b'\r\n')
    return b''

def git(*args, data=None):
    r = subprocess.run(['git', '-C', src, *args], input=data, capture_output=True)
    return r.stdout if r.returncode == 0 else b''

def committed(rel, data):
    if rel == 'CLAUDE.md':
        revs = git('log', '--format=%H', 'HEAD', '--', WISDOM).decode().split()
        return any(body(git('show', f'{r}:{WISDOM}')) == data for r in revs)
    oid = git('hash-object', '--stdin', data=data).strip().decode()
    return bool(oid) and bool(git('log', '-1', '--format=%H', '--find-object=' + oid, 'HEAD', '--', rel).strip())

def merged(rel, data, s, m):  # the repo copy already holds every live change
    base = git('show', f'{commit}:{WISDOM if rel == "CLAUDE.md" else rel}') if commit else b''
    base = body(base) if rel == 'CLAUDE.md' else base
    if not base or sha(base) != m:
        return False
    os.makedirs(tmp, exist_ok=True)
    for name, b in (('repo', s), ('base', base), ('live', data)):
        with open(os.path.join(tmp, name), 'wb') as f:
            f.write(b)
    r = subprocess.run(['git', 'merge-file', '-p', *(os.path.join(tmp, n) for n in ('repo', 'base', 'live'))],
                       capture_output=True)
    return r.returncode == 0 and r.stdout == s

def source(rel):
    if rel == 'CLAUDE.md':
        return body(read(os.path.join(src, WISDOM)))
    p = os.path.join(src, rel)
    return None if rel.startswith('skills/global/') or not os.path.isfile(p) else read(p)

def prefixes(rel):
    parts = rel.split('/')
    return ['/'.join(parts[:i]) for i in range(1, len(parts) + 1)]

def retired(rel):  # a dropped name, or a legacy nested skills/<name>/<name>/ copy
    parts = rel.split('/')
    return any(p in RETIRED for p in prefixes(rel)) or (
        len(parts) > 3 and parts[0] == 'skills' and parts[1] == parts[2])

def kept(rel):
    return any(p in keepset for p in prefixes(rel))

def shadowed(rel):  # the source has the kept path itself, as a file or a dir
    return any(os.path.lexists(os.path.join(src, p))
               for p in prefixes(rel) if p in keepset)

def fail(err):  # an unreadable dir must stop the run, not hide its files
    sys.exit(f'Cannot read {err.filename}: {err.strerror}')

mpath = os.path.join(live, 'kronael-install-manifest.json')
manifest = json.loads(read(mpath)) if os.path.isfile(mpath) else {}
files, commit = manifest.get('files', {}), manifest.get('release', {}).get('gitCommit')
keepset = set(keep.expand(live))

paths, links = [], []
for r in ('CLAUDE.md', 'RECLAUDE.md', *keep.DIRS):
    top = os.path.join(live, r)
    if os.path.islink(top):
        links.append(r)
    elif r in keep.DIRS and os.path.lexists(top):
        for root, dirs, names in os.walk(top, onerror=fail):
            subs = [x for x in dirs if os.path.islink(os.path.join(root, x))]
            dirs[:] = [x for x in dirs if x not in subs]
            for n in names + subs:
                rel = os.path.relpath(os.path.join(root, n), live)
                if os.path.islink(os.path.join(root, n)) and not kept(rel):
                    links.append(rel)
                else:
                    paths.append(rel)
    elif os.path.lexists(top):
        paths.append(r)

counts, out, only = {}, [], set()
for rel in sorted(paths):
    s = source(rel)
    if set(rel.split('/')) & JUNK or rel.endswith('.pyc'):
        cls = 'junk'
    elif kept(rel):
        cls = 'shadow' if shadowed(rel) else 'kept'
    elif s is None and retired(rel):
        cls = 'retired'
    elif s is None:
        cls = 'only-live'
        only.add(next((p for p in prefixes(rel) if p == 'skills/global'
                       or not os.path.lexists(os.path.join(src, p))), rel))
    else:
        data = read(os.path.join(live, rel))
        i, m = sha(data), files.get('.claude/' + rel, {}).get('source_sha256')
        cls = ('same' if i == sha(s) else 'stale' if i == m or committed(rel, data)
               else 'no-base' if m is None else 'edited' if sha(s) == m
               else 'merged' if merged(rel, data, s, m) else 'both')
    counts[cls] = counts.get(cls, 0) + 1
    if cls in ('edited', 'both', 'no-base', 'shadow'):
        out.append(f'{cls:9} {rel}')
out += [f'only-live {p}' for p in sorted(only)]
out += [f'kept      {p}' for p in sorted(keepset)]
out += [f'SYMLINK {p}' for p in sorted(links)]

pat = re.compile(r'(?:~|\$HOME|' + re.escape(home) + r')/\.claude/((?:' + '|'.join(keep.DIRS) + r')/[^\s"\';|&]+)')
for name in ('settings.json', 'settings.local.json'):
    p = os.path.join(live, name)
    for rel in pat.findall(read(p).decode()) if os.path.isfile(p) else []:
        if not os.path.exists(os.path.join(src, rel)) and not kept(rel):
            out.append(f'UNRESOLVED {name}: ~/.claude/{rel}')
print(' '.join(f'{k}={v}' for k, v in sorted(counts.items())) or 'no live bundle files')
if out:
    print('\n'.join(out))
sys.exit(1 if any(o.startswith(('UNRESOLVED', 'SYMLINK')) for o in out) else 0)
PY
```

## Merge one `both` path (step 2)

`P` is the path under `~/.claude/` — the source path is the same, except
`CLAUDE.md`, whose source is the body of `skills/global/SKILL.md`. Build the
base and repo copies in `$RUN/merge/`, check the base is what the last sync
wrote, then let git merge:

```sh
P=<path>; S=$P; mkdir -p "$RUN/merge"
f() { if [ "$P" = CLAUDE.md ]; then awk 'n>=2 && (p || NF) {p=1; print} /^---$/{n++}'; else cat; fi; }
m() { python3 -c 'import json, os, sys
d = json.load(open(os.path.expanduser("~/.claude/kronael-install-manifest.json")))
print(d["release"]["gitCommit"] if sys.argv[1] == "commit" else
      d["files"].get(".claude/" + sys.argv[1], {}).get("source_sha256", ""))' "$1"; }
[ "$P" = CLAUDE.md ] && S=skills/global/SKILL.md
git -C "$SRC" show "$(m commit):$S" | f > "$RUN/merge/base"
f < "$SRC/$S" > "$RUN/merge/repo"
if [ "$(sha256sum < "$RUN/merge/base" | cut -c1-64)" = "$(m "$P")" ]; then
  git merge-file -L repo -L base -L live "$RUN/merge/repo" "$RUN/merge/base" ~/.claude/"$P"; echo "conflicts=$?"
else
  echo "NO BASE: handle $P as no-base"
fi
```

`conflicts=0` is a clean merge in `$RUN/merge/repo`; `conflicts=N` leaves N
conflict blocks there to resolve with the owner. Then write it into the repo —
for `CLAUDE.md`, behind the original frontmatter:

```sh
if [ "$P" = CLAUDE.md ]; then
  { awk '{print} /^---$/ && ++n==2 {exit}' "$SRC/$S"; echo; cat "$RUN/merge/repo"; } > "$RUN/merge/global"
  mv "$RUN/merge/global" "$SRC/$S"
else
  cp "$RUN/merge/repo" "$SRC/$S"
fi
```

## Swap (step 4)

ONE Bash invocation, never split. It builds the new bundle on the same
filesystem as `~/.claude/`, then exchanges each bundle path with its new copy
in one `renameat2(RENAME_EXCHANGE)` call, so no path is ever missing — a
`mv` pair leaves a gap that a hook firing in another session can hit. Linux
only: elsewhere the first exchange fails and nothing has moved.

```sh
set -euo pipefail
L="$HOME/.claude"
die() { echo "Swap refused: $*" >&2; exit 1; }
[[ -d "$SRC/skills" && -f "$RUN/keep.py" ]] || die "need SRC/skills and RUN/keep.py"
[[ ! -e "$RUN/old" ]] || die "$RUN/old exists: use a new run dir"
[[ ! -e "$L/.kronael-sync-new" && ! -e "$L/.kronael-sync-old" ]] ||
  die "a .kronael-sync-* dir is left in $L: step 0"
python3 "$RUN/keep.py" || die "fix $L/.keep (the lines above)"
mkdir -p "$L"
mkdir "$L/.kronael-sync-new" "$L/.kronael-sync-old"
aside() {
  mv "$L/.kronael-sync-new" "$RUN/failed-$$"
  rmdir "$L/.kronael-sync-old"
  echo "Swap failed: $L is as it was; the unused build is in $RUN/failed-$$" >&2
}
trap aside EXIT
tar -C "$SRC" --exclude=__pycache__ --exclude=.pytest_cache --exclude=.ruff_cache \
  --exclude=.claude --exclude=skills/global \
  -cf - skills agents hooks output-styles commands RECLAUDE.md \
  | tar -C "$L/.kronael-sync-new" -xf -
awk 'n>=2 && (p || NF) {p=1; print} /^---$/{n++}' "$SRC/skills/global/SKILL.md" \
  > "$L/.kronael-sync-new/CLAUDE.md"
trap - EXIT
PYTHONPATH="$RUN" python3 -B - <<'PY' || { s=$?; [[ $s -ne 1 ]] || aside; exit "$s"; }
import ctypes, hashlib, json, os, re, shutil, signal, subprocess, sys, time
sys.path.insert(0, os.environ['RUN'])  # ahead of the CWD entry `python3 -` adds
import keep
src, live = os.environ['SRC'], os.path.expanduser('~/.claude')
new, old = os.path.join(live, '.kronael-sync-new'), os.path.join(live, '.kronael-sync-old')
PATHS = (*keep.DIRS, 'CLAUDE.md', 'RECLAUDE.md', 'kronael-install-manifest.json')
links = [p for p in PATHS if os.path.islink(os.path.join(live, p))]
if links:
    raise SystemExit(f'live {links} are symlinks (Classify: SYMLINK); nothing moved')
AT_FDCWD, RENAME_EXCHANGE = -100, 2

def git(*args):
    r = subprocess.run(['git', '-C', src, *args], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else None

def fail(err):
    raise err

files = {}  # the manifest lists source files only: it is written before the keep-list copy
for root, _, names in os.walk(new, onerror=fail):
    for n in names:
        rel = os.path.relpath(os.path.join(root, n), new)
        with open(os.path.join(root, n), 'rb') as f:
            files['.claude/' + rel] = {'source': 'skills/global/SKILL.md' if rel == 'CLAUDE.md' else rel,
                                       'source_sha256': hashlib.sha256(f.read()).hexdigest()}
log = os.path.join(src, 'CHANGELOG.md')
m = re.search(r'^## \[(v[0-9.]+)\]', open(log).read(), re.M) if os.path.isfile(log) else None
release = {'version': m.group(1) if m else None, 'gitCommit': git('rev-parse', 'HEAD'),
           'gitDescribe': git('describe', '--tags', '--dirty'),
           'installedAt': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}
with open(os.path.join(new, 'kronael-install-manifest.json'), 'w') as f:
    json.dump({'version': 1, 'release': release, 'files': dict(sorted(files.items()))}, f, indent=1)

kept = keep.expand(live)
shadows = [p for p in kept if os.path.lexists(os.path.join(src, p))]
if shadows:
    raise SystemExit(f'Swap refused: kept {shadows} shadow the source (step 3)')
for p in kept:
    s, d = os.path.join(live, p), os.path.join(new, p)
    os.makedirs(os.path.dirname(d), exist_ok=True)
    if os.path.isdir(s) and not os.path.islink(s):
        shutil.copytree(s, d, symlinks=True)
    else:
        shutil.copy2(s, d, follow_symlinks=False)

missing = [p for p in PATHS if not os.path.lexists(os.path.join(new, p))]
if missing:
    raise SystemExit(f'new bundle lacks {missing}; nothing moved')
libc = ctypes.CDLL(None, use_errno=True)

def exchange(a, b):
    r = libc.renameat2(AT_FDCWD, a.encode(), AT_FDCWD, b.encode(), RENAME_EXCHANGE)
    if r != 0:
        raise OSError(ctypes.get_errno(), f'exchange {a} {b}')

signal.pthread_sigmask(signal.SIG_BLOCK,
                       {signal.SIGINT, signal.SIGTERM, signal.SIGHUP})
swapped = []  # (path, where its old copy sits: None when live had none)
try:
    for p in PATHS:
        a, b = os.path.join(new, p), os.path.join(live, p)
        if not os.path.lexists(b):
            os.rename(a, b)
            swapped.append((p, None))
            continue
        exchange(a, b)
        swapped.append((p, a))
        os.rename(a, os.path.join(old, p))
        swapped[-1] = (p, os.path.join(old, p))
except Exception as err:
    failed = p
    try:
        while swapped:
            p, at = swapped[-1]
            a, b = os.path.join(new, p), os.path.join(live, p)
            if at is None:
                os.rename(b, a)
            else:
                exchange(at, b)
                if at != a:
                    os.rename(at, a)
            swapped.pop()
    except Exception as undo:
        left = [p for p, _ in swapped]
        print(f'ROLLBACK FAILED: {undo}\nstill swapped: {left}; '
              f'their old copies are in {new} or {old} (step 0)', file=sys.stderr)
        sys.exit(2)
    sys.exit(f'Swap failed at {failed}: {err}; every exchanged path restored')
PY
rmdir "$L/.kronael-sync-new"
mv "$L/.kronael-sync-old" "$RUN/old"
echo "swap ok, previous bundle in $RUN/old"
```

A failure leaves `~/.claude/` as it started — before the exchange loop
nothing live has moved, and a failure inside it exchanges every swapped path
back — and prints `Swap failed:` with the unused build moved to
`$RUN/failed-<pid>`. The Python part exits 1 exactly when nothing live has
changed, which is when the build moves aside. The `.kronael-sync-*` dirs stay
only when the rollback fails (`ROLLBACK FAILED`, exit 2, naming the paths
still swapped) or the run is killed; step 0 handles both. The loop blocks
SIGINT, SIGTERM and SIGHUP, so a signal cannot stop it halfway.

## Codex bridge (step 6)

- Global guidance: `~/.codex/AGENTS.md` is a REAL file holding the marked
  block from `codex/AGENTS.md`, which tells Codex to read
  `~/.claude/CLAUDE.md`. Absent → copy `codex/AGENTS.md` there. A symlink
  resolving to `~/.claude/CLAUDE.md` → replace it with that copy; any other
  symlink → conflict, show and ask. Existing real file → replace only the
  Kronael block, else append it; NEVER overwrite content outside the markers.
  An existing `~/.codex/AGENTS.override.md` shadows `AGENTS.md` — conflict,
  show and ask. NEVER rely on project fallback names for global guidance.
- `~/.codex/config.toml`: ensure top-level `project_doc_fallback_filenames`
  contains `CLAUDE.md` (before the first `[table]`; NEVER under `[tui]` etc.).
- Symlink `~/.agents/skills` → `~/.claude/skills`. Per-skill symlinks only if
  it is already a directory; there, `rm` each per-skill symlink that no
  longer resolves (`find ~/.agents/skills -maxdepth 1 -xtype l` lists them).
  If pi is installed, symlink `~/.pi/agent/AGENTS.md` → `~/.claude/CLAUDE.md`
  (skip if a real file exists).
- Copy `codex-hooks.json` → `~/.codex/hooks.json`. It wires Codex's lifecycle
  events into `~/.claude/hooks/codex_hook.py`, which normalizes Codex payloads
  before delegating to the Kronael hooks (and drops context-only output for
  Codex `PreCompact`, which only accepts block decisions).
- Tell the user to open `/hooks` in the next Codex TUI session and trust the
  changed hooks. One-shot verify only: `--dangerously-bypass-hook-trust`.

## External tool commands (step 7)

Run `which <tool>` first; skip if present and recent.

**Core** — ask once, install as a batch:

| Tool | Command | Skills |
|------|---------|--------|
| `ship` | `uv tool install git+https://github.com/kronael/ship` | /ship |
| `agent-browser` | `bun install -g agent-browser` | /browse |
| `codex` | `bun install -g @openai/codex` | /astra /oracle |
| `pi` | `bun install -g @mariozechner/pi-coding-agent` — then verify `pi --version` runs; see the note below | /pi |
| `pyright` | `bun install -g pyright` | /py /ts /tsx |
| `typescript-language-server` | `bun install -g typescript typescript-language-server` | /ts /tsx |
| `pre-commit` | `uv tool install pre-commit` | all (hooks) |
| `ast-grep` | `uv tool install ast-grep-cli && rm -f ~/.local/bin/sg` | /astgrep |

`pi` ships a `#!/usr/bin/env node` shebang but its TUI uses the `v` regex flag,
which needs Node 20+. On an older system node every invocation dies with
`SyntaxError: Invalid regular expression flags`, `--version` included. bun runs
it regardless, so when `pi --version` fails, put a wrapper earlier on PATH than
`~/.bun/bin`:

```bash
cat > ~/.local/bin/pi <<'SH'
#!/usr/bin/env bash
set -euo pipefail
exec "$HOME/.bun/bin/bun" "$HOME/.bun/install/global/node_modules/@mariozechner/pi-coding-agent/dist/cli.js" "$@"
SH
chmod +x ~/.local/bin/pi
```

**Security audit** — ask separately (large, optional):

| Tool | Command | Skills |
|------|---------|--------|
| `bandit` | `uv tool install bandit` | /eval (red) |
| `pip-audit` | `uv tool install pip-audit` | /eval (red) |
| `semgrep` | `uv tool install semgrep` | /eval (red) |
| `govulncheck` | `go install golang.org/x/vuln/cmd/govulncheck@latest` | /eval (red) |
| `trufflehog` | download `linux_amd64.tar.gz` from github.com/trufflesecurity/trufflehog/releases into `~/.local/bin` (NOT `go install` — its go.mod `replace` directives make `go install` refuse) | /eval (red) |
| `gitleaks` | download from github.com/gitleaks/gitleaks releases | /eval (red) |

**Video rendering** — ask separately (heavy, rarely needed):

| Tool | Command | Skills |
|------|---------|--------|
| `faster-whisper` | library, no CLI — the render script pulls it via `uv run --with faster-whisper`; NEVER `uv tool install` it (no entrypoints) | /create (video render) |

## ripwire — deterministic codebase maps for agents (step 7)

Optional, ask separately. `ripwire` (redhat-et, Apache-2.0) hands a coding
agent a ranked, deterministic call-graph map of a repo — relevant symbols,
callers, change-risk, tests to run — instead of blind grepping. Offline C++
binary: no API key, no embeddings, no daemon, no network calls. Install the
prebuilt binary (the installer verifies a mandatory sha256 and prompts for
consent):

```sh
RIPWIRE_REPO=redhat-et/ripwire bash -c "$(curl -fsSL https://raw.githubusercontent.com/redhat-et/ripwire/main/scripts/install.sh)"
```

- Installs `ripwire` to `~/.local/bin` and auto-symlinks its `ripwire-*`
  skills into `~/.claude/skills` — namespaced, so they never collide with
  kronael skills. As symlinks they survive every sync without a keep-list
  line. It also detects `~/.codex`/`~/.agents` and activates for
  Codex.
- Its data-logging hooks stay OFF (gated behind an explicit `--hook`; even
  armed they log only a local hashed routing meter, never prompt/command/path
  text, `RIPWIRE_ROUTE_METER=0` to disable). Leave hooks off to keep it silent.
- `RIPWIRE_NO_ACTIVATE=1` installs the binary only, touching no agent config.
- MCP (optional second interface — CLI + skills already work without it). Use
  ripwire's own recipe printer `ripwire wrap <agent>`; it PRINTS the exact line
  and never edits any config — you run it:
  - Claude Code: `ripwire wrap claude` → `claude mcp add ripwire -- ripwire --mcp`
    (append `--scope user` for all projects; writes `mcpServers` into
    `~/.claude.json`, NOT `settings.json`). NEVER put `mcpServers` in
    `settings-recommended.json`.
  - Codex: `ripwire wrap codex` → a `[mcp_servers.ripwire]` stanza for
    `~/.codex/config.toml` (CLI-first; MCP restricted to audit/health verbs).
  - `ripwire wrap --all` detects every installed agent and emits each config.

## CLI tools (step 8)

Install the repo's standalone CLI tools so their `~/.local/bin` binaries track
the repo (a stale binary is the failure this prevents). ONLY when the tool's
source dir exists at the source root (clone/manual path; the Codex marketplace
snapshot carries them too). A plugin-only snapshot omits them — say so and
point to `cd <tool> && make install` from a clone. Each Makefile is idempotent,
so ALWAYS (re)install to refresh a stale binary. NEVER fail the whole sync if
one toolchain is missing — report that tool skipped and continue.

| Tool | Command | Notes |
|------|---------|-------|
| `rig` | `cd rig && make install` | git helpers: rig + rip/rco/rir/rim |
| `udfix` | `cd udfix && make install` | needs a Go toolchain |
| CDPATH | the block below, in `~/.bashrc` | `cd <project>` from `~/app`, `~/wk`, `~/sandbox`; always |
| `dockbox` | `cd dockbox && make install` | builds a Docker image — needs Docker; ask separately |

The CDPATH block is a plain shell variable, not exported by the block: a
script that inherits CDPATH can `cd` somewhere unexpected. Its first entry is
empty, not `.`: the current directory still wins, and a `cd` into a local
directory prints nothing, so `$(cd sub && pwd)` stays one line. A root that does not exist is
skipped by `cd`. Write or replace the block; a symlinked `~/.bashrc` is edited
through the link:

```sh
python3 - <<'PY'
import os, re
p = os.path.expanduser('~/.bashrc')
BEGIN, END = '# >>> kronael cdpath >>>', '# <<< kronael cdpath <<<'
block = [BEGIN, 'CDPATH=:$HOME/app:$HOME/wk:$HOME/sandbox', END]
lines = open(p).read().splitlines() if os.path.exists(p) else []
if BEGIN in lines and END in lines[lines.index(BEGIN):]:
    i = lines.index(BEGIN)
    lines[i:lines.index(END, i) + 1] = block
elif BEGIN in lines or END in lines:
    raise SystemExit(f'{p}: a kronael cdpath marker without its pair; fix it by hand')
else:
    lines += ([''] if lines else []) + block
open(p, 'w').write('\n'.join(lines) + '\n')
others = [l for l in lines if re.match(r'\s*(export\s+)?CDPATH\b', l) and l != block[1]]
print('CDPATH block written' + (f'; ~/.bashrc also sets it: {others}' if others else ''))
PY
```

## Server memory

For opted-in first syncs only, follow `skills/server-init/SKILL.md` at the
source root after the bundle and tools are installed. It scans the host
read-only and writes `~/.claude/skills/server-<hostname>/`. NEVER run it when
`CLAUDE_SANDBOX` is set: the launcher writes the box's sandbox note.
