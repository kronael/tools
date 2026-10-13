#!/usr/bin/env python3
"""Lint a `specs/` corpus against the `specs` skill (`skills/specs/format.md`).

The rules are format.md's self-review checklist, mechanically. Each finding
names its rule and points back at format.md so a failure teaches. Errors fail
the run; warnings only print — English tense, wording and path-shaped
backticks are guesses, and a false hard-fail trains `--no-verify`.

Checklist item 3, "No HOW (implementation steps)", has no rule on purpose: it
is a judgement call, and a lint that guesses at it is wrong loudly.

Exit codes: 0 no errors (warnings may print), 1 at least one error,
2 a path does not exist or the arguments are wrong.
"""

from __future__ import annotations

import argparse
import functools
import os
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from urllib.parse import unquote

STATUSES = ('draft', 'experiment', 'planned', 'partial', 'shipped', 'reference')
OPEN_STATUSES = frozenset({'draft', 'reference'})
POINTED_STATUSES = frozenset({'partial', 'shipped'})
NUMBERED = re.compile(r'^(\d+)-[a-z0-9]+(?:-[a-z0-9]+)*\.md$')
NOT_SPECS = frozenset({'index.md', 'CLAUDE.md'})
FLAT_PAD = 2
PHASE_DEPTH = 2
LONG = 500
TOO_LONG = 1000
BOUNDARY = re.compile(r'^---\s*$', re.MULTILINE)
STATUS = re.compile(r'^status:\s*([^#]*?)\s*(?:#.*)?$', re.MULTILINE)
LINK = re.compile(r'\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
SCHEME = re.compile(r'^[a-z][a-z0-9+.-]*:')
FENCE = re.compile(r'^\s*(`{3,}|~{3,})')
TBD = re.compile(r'\bTBD\b|\bTODO\b|(?i:implement later)')
FUTURE = re.compile(r"\bwe will\b|\bwe'll\b|\bwill be\b", re.IGNORECASE)
HISTORY = re.compile(
    r'\bno longer\b|\bformerly\b|\brenamed from\b|\bused to be\b|\bas before\b'
    r'|\bbackwards?[- ]compat',
    re.IGNORECASE,
)
WORDING = (
    (re.compile(r'\bharness(?:es)?\b', re.IGNORECASE), 'say "tests" or "the script"'),
    (
        re.compile(
            r'\b(?:powerful|seamless(?:ly)?|robust(?:ly|ness)?|cutting-edge|best-in-class'
            r'|state-of-the-art|world-class|blazing(?:ly)? fast|excited to)\b',
            re.IGNORECASE,
        ),
        'marketing — state the behaviour',
    ),
)
OPTIONS = re.compile(
    r'^#{1,6}\s+(?:(?i:alternatives?|variants?)\b'
    r'|.*\b(?:Option|Alternative|Approach|Variant) [A-Z0-9]\b)'
)
OPEN_QUESTIONS = re.compile(
    r'^#{1,6}\s.*\b(?:open questions?|unresolved|undecided)\b', re.IGNORECASE
)
CHECKLIST = re.compile(r'^\s*[-*+] \[[ xX]\] ')
CREATE_TABLE = re.compile(r'\bcreate table (?:if not exists )?([a-z_][a-z0-9_.]*)', re.IGNORECASE)
TICKED = re.compile(r'`([^`\n]+)`')
AT_LINE = re.compile(r':(\d+)(?:-(\d+))?$')
SUFFIX = re.compile(r'\.[a-z][a-z0-9+]{0,9}$')
NOT_IN_PATH = frozenset(' \t*?{}<>$|"\'()[]=,;!`')
PLACEHOLDER = re.compile(r'(?:^|/)(?:YYYYMMDD|NN)(?:[-_.]|$)')
SKIP_DIRS = frozenset(
    {
        '.git',
        'node_modules',
        '.venv',
        'venv',
        '__pycache__',
        '.cache',
        '.pytest_cache',
        '.mypy_cache',
        '.ruff_cache',
        '.next',
        '.tox',
        'dist',
        'build',
        'target',
    }
)

RULES_HELP = """\
paths: a specs dir is checked as it is; a spec file or a project dir is
searched for corpora, a dir named specs holding an index.md or a numbered
spec file (so a test suite named specs is left alone).

rules (format.md owns the wording):
  spec-naming          <NN>-<topic>.md flat or <phase>/<N>-<topic>.md   error
                       two files share a number                         error
                       flat number not zero-padded                     warn
  spec-status          frontmatter status outside the closed vocabulary error
                       index Status cell differs from the file          error
  spec-index-row       spec without a row in index.md or its phase index error
  spec-index-dangling  index link to a file that does not exist        error
  spec-link            spec link to a file that does not exist         error
  spec-table-owner     CREATE TABLE <name> in two specs                 error
  spec-length          over 1000 lines                                  error
                       over 500 lines                                   warn
  spec-tbd             TBD, TODO, implement later                      error
  spec-future-tense    we will, we'll, will be                         warn
  spec-history         no longer, formerly, renamed from, used to be,   warn
                       as before, backward compatibility
  spec-wording         harness; marketing words                        warn
  spec-options         a heading laying out options or alternatives    warn
  spec-open-questions  an open-questions heading outside draft         warn
  spec-checklist       a task-list item                                 warn
  spec-pointer         `path` or `path:line` stale, ambiguous or past   warn
                       the end of the file
  spec-no-pointer      a partial or shipped spec names no file         warn

exit codes: 0 no errors, 1 errors found, 2 bad path or arguments
"""


class Severity(Enum):
    ERROR = 'error'
    WARN = 'warn'


@dataclass(frozen=True)
class Finding:
    severity: Severity
    rule: str
    message: str


def finding(severity: Severity, rule: str, where: Path, line: int, text: str) -> Finding:
    return Finding(severity, rule, f'{where}:{line}: [{rule}] {text}')


def is_spec_corpus(path: Path) -> bool:
    """A dir named specs that holds an index or a numbered spec file.

    A test suite in `e2e/specs/` or a skill's own `skills/specs/` is also a
    directory named specs; requiring an index or one numbered file keeps both
    off discovery and off `nearest_root()`.
    """
    numbered = any(NUMBERED.match(child.name) for child in path.glob('*.md'))
    return (path / 'index.md').is_file() or numbered


def walk(top: Path) -> list[tuple[Path, list[str]]]:
    """Every directory under `top` with its file names, skipping generated dirs
    and nested repositories: a dir holding its own `.git` is another checkout.
    """
    found: list[tuple[Path, list[str]]] = []
    for dirpath, dirnames, filenames in os.walk(top):
        here = Path(dirpath)
        dirnames[:] = [
            d for d in dirnames if d not in SKIP_DIRS and not (here / d / '.git').exists()
        ]
        found.append((here, filenames))
    return found


def nearest_root(path: Path) -> Path | None:
    for candidate in (path, *path.parents):
        if candidate.name == 'specs' and candidate.is_dir() and is_spec_corpus(candidate):
            return candidate
    return None


def discovered(root: Path) -> list[Path]:
    return [here for here, _ in walk(root) if here.name == 'specs' and is_spec_corpus(here)]


def spec_roots(paths: list[Path]) -> list[Path]:
    """Explicit specs dirs are checked; discovery requires a corpus marker."""
    roots: list[Path] = []
    for path in paths:
        if path.is_dir() and path.name == 'specs':
            roots.append(path)
            continue
        target = path.parent if path.is_file() else path
        named = nearest_root(target)
        if named is not None:
            roots.append(named)
            continue
        roots.extend(discovered(target))
    return sorted(set(roots))


def spec_files(root: Path) -> list[Path]:
    """Every spec file: `.md` under the corpus except the indexes and
    `CLAUDE.md`, which Claude Code reads as directory instructions.
    """
    return sorted(
        path
        for path in root.glob('**/*.md')
        if path.name not in NOT_SPECS and not SKIP_DIRS & set(path.relative_to(root).parts)
    )


def frontmatter(text: str) -> tuple[str, str] | None:
    if not text.startswith('---\n'):
        return None
    match = BOUNDARY.search(text, 4)
    if match is None:
        return None
    return text[4 : match.start()], text[match.end() :].lstrip('\n')


def status_of(text: str) -> str | None:
    """The frontmatter `status` value: '' when the key is missing, None when
    the file has no frontmatter at all.
    """
    split = frontmatter(text)
    if split is None:
        return None
    match = STATUS.search(split[0])
    return match.group(1).strip('\'"') if match else ''


def split_fences(text: str) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    """Numbered lines outside fenced blocks, then the lines inside them — a
    fence quotes code, not spec prose.
    """
    outside: list[tuple[int, str]] = []
    inside: list[tuple[int, str]] = []
    opened = ''
    for number, line in enumerate(text.splitlines(), start=1):
        fence = FENCE.match(line)
        if fence and not opened:
            opened = fence.group(1)
            continue
        if fence and fence.group(1)[0] == opened[0] and len(fence.group(1)) >= len(opened):
            opened = ''
            continue
        (inside if opened else outside).append((number, line))
    return outside, inside


def prose(text: str) -> list[tuple[int, str]]:
    return split_fences(text)[0]


def row_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith('|') or not stripped.endswith('|'):
        return []
    return [cell.strip() for cell in stripped[1:-1].split('|')]


def link_target(target: str) -> str | None:
    """The file a markdown link names, or None for a URL, an anchor, a
    `scheme:` reference or a placeholder.
    """
    if '://' in target or target.startswith('#') or SCHEME.match(target):
        return None
    if set(target) & set('<>{}$'):
        return None
    return unquote(target.split('#')[0])


def link_file(named: str, beside: Path, repo: Path) -> Path:
    """The file a link names: from the repo root when it starts with `/`, as
    GitHub reads it, else beside the linking file.
    """
    return repo / named.lstrip('/') if named.startswith('/') else beside / named


def pointer_path(token: str) -> str | None:
    """The path a backticked token points at, or None.

    A pointer is `path:line` or a backticked path with a slash — a bare
    `config.yaml` reads as a kind of file more often than a place in this repo.
    An extension is lowercase, which keeps `net/http.Server` out. A segment
    that is itself a documented placeholder (PLACEHOLDER) names a shape, not a
    file, and is never meant to resolve.
    """
    if NOT_IN_PATH & set(token) or '://' in token or '..' in token:
        return None
    if token.startswith(('/', '~', '-', '#', '@', ':')):
        return None
    path = AT_LINE.sub('', token)
    if SUFFIX.search(path) is None:
        return None
    if '/' not in path and path == token:
        return None
    if PLACEHOLDER.search(path):
        return None
    return path


def names_file(token: str) -> bool:
    """A backticked token shaped like a file: a pointer, or a bare `name.ext`."""
    if pointer_path(token) is not None:
        return True
    return not NOT_IN_PATH & set(token) and '://' not in token and SUFFIX.search(token) is not None


def repo_root(component: Path) -> Path:
    """The nearest ancestor holding `.git` (a dir, or a worktree's file), else
    the component itself.
    """
    for candidate in (component, *component.parents):
        if (candidate / '.git').exists():
            return candidate
    return component


@functools.cache
def indexed_files(repo: Path) -> dict[str, list[Path]]:
    """Every file under the repo by basename, relative to it."""
    by_name: dict[str, list[Path]] = {}
    for here, filenames in walk(repo):
        for name in filenames:
            by_name.setdefault(name, []).append((here / name).relative_to(repo))
    return by_name


@functools.cache
def line_count(path: Path) -> int:
    return len(path.read_bytes().splitlines())


def resolve_pointer(pointer: str, spec: Path, root: Path) -> list[Path]:
    """The files a pointer names: one when it resolves, none when it is stale,
    several when it is ambiguous.

    Resolution is direct from the spec's own dir, the corpus, the component
    (the dir holding `specs/`) and each ancestor up to the repo root; failing
    that, by trailing path segments anywhere in the repo — a bare `name.py:12`
    resolves when one file has that name — preferring the component's files.
    """
    spec = spec.absolute()
    root = root.absolute()
    component = root.parent
    repo = repo_root(component)
    bases = [spec.parent, root, component]
    while bases[-1] != repo:
        bases.append(bases[-1].parent)
    for base in bases:
        if (base / pointer).exists():
            return [base / pointer]
    parts = Path(pointer).parts
    tails = [
        repo / rel
        for rel in indexed_files(repo).get(parts[-1], [])
        if rel.parts[-len(parts) :] == parts
    ]
    if len(tails) > 1:
        inside = [path for path in tails if path.is_relative_to(component)]
        return inside or tails
    return tails


def check_naming(root: Path, path: Path) -> list[Finding]:
    parts = path.relative_to(root).parts
    shape = 'format.md: specs/<NN>-<topic>.md flat, or specs/<phase>/<N>-<topic>.md'
    if len(parts) > PHASE_DEPTH:
        text = f'{len(parts) - 1} directories below specs/ — {shape}'
        return [finding(Severity.ERROR, 'spec-naming', path, 1, text)]
    match = NUMBERED.match(parts[-1])
    if match is None:
        text = (
            f'name {parts[-1]!r} is not <number>-<kebab-topic>.md '
            '— format.md: NEVER use an unnumbered by-content name'
        )
        return [finding(Severity.ERROR, 'spec-naming', path, 1, text)]
    if len(parts) == 1 and len(match.group(1)) < FLAT_PAD:
        text = (
            f'flat number {match.group(1)!r} is not zero-padded '
            '— format.md: NN a zero-padded integer, the first is 01 (warn)'
        )
        return [finding(Severity.WARN, 'spec-naming', path, 1, text)]
    return []


def check_numbers(files: list[Path]) -> list[Finding]:
    """Two spec files in one directory never share a number: "spec 3" names one file."""
    by_number: dict[tuple[Path, int], list[Path]] = {}
    for path in files:
        match = NUMBERED.match(path.name)
        if match is not None:
            by_number.setdefault((path.parent, int(match.group(1))), []).append(path)
    findings: list[Finding] = []
    for paths in by_number.values():
        if len(paths) < 2:
            continue
        others = ', '.join(path.name for path in paths[1:])
        text = (
            f"number shared with {others} — format.md: the number is the spec's handle, "
            'one file per number'
        )
        findings.append(finding(Severity.ERROR, 'spec-naming', paths[0], 1, text))
    return findings


def check_status(path: Path, text: str) -> list[Finding]:
    status = status_of(text)
    if status is None:
        message = 'no YAML frontmatter — format.md: every spec file starts with `status:`'
        return [finding(Severity.ERROR, 'spec-status', path, 1, message)]
    if status in STATUSES:
        return []
    message = (
        f'status {status!r} is not one of {", ".join(STATUSES)} '
        '— format.md defines the complete set'
    )
    return [finding(Severity.ERROR, 'spec-status', path, 1, message)]


def check_length(path: Path, text: str) -> list[Finding]:
    lines = len(text.splitlines())
    if lines > TOO_LONG:
        message = f'{lines} lines — format.md: a spec is tables with `file:line` anchors, not prose'
        return [finding(Severity.ERROR, 'spec-length', path, 1, message)]
    if lines > LONG:
        message = (
            f'{lines} lines, over {LONG} — format.md: tables with `file:line` anchors '
            'over prose; cut HOW, keep WHY and WHERE (warn)'
        )
        return [finding(Severity.WARN, 'spec-length', path, 1, message)]
    return []


def linked_files(line: str, beside: Path, repo: Path) -> list[tuple[str, Path]]:
    """Each file link on the line with the file it names; URLs, anchors and
    scheme references are left out.
    """
    found: list[tuple[str, Path]] = []
    for target in LINK.findall(line):
        named = link_target(target)
        if named is not None:
            found.append((target, link_file(named, beside, repo)))
    return found


def phase_indexes(index: Path, repo: Path) -> list[Path]:
    """The `<phase>/index.md` files the root index links."""
    found: list[Path] = []
    for _, line in prose(index.read_text()):
        for _, candidate in linked_files(line, index.parent, repo):
            if candidate.name == 'index.md' and candidate.is_file() and candidate != index:
                found.append(candidate)
    return found


def check_one_index(index: Path, specs: set[Path], repo: Path) -> tuple[list[Finding], set[Path]]:
    """Dangling links and Status cells in one index; the specs it lists."""
    findings: list[Finding] = []
    linked: set[Path] = set()
    for number, line in prose(index.read_text()):
        for target, named in linked_files(line, index.parent, repo):
            if not named.exists():
                message = (
                    f'link {target!r} resolves to nothing — format.md: index.md is the '
                    'master table of the files present'
                )
                findings.append(
                    finding(Severity.ERROR, 'spec-index-dangling', index, number, message)
                )
        cells = row_cells(line)
        if len(cells) < 3:
            continue
        rows = [named.resolve() for _, named in linked_files(cells[0], index.parent, repo)]
        spec = next((row for row in rows if row in specs), None)
        if spec is None:
            continue
        linked.add(spec)
        if cells[1] not in STATUSES:
            message = (
                f'index Status cell {cells[1]!r} is not one of {", ".join(STATUSES)} '
                '— format.md: the Status column carries the lifecycle value, not prose'
            )
            findings.append(finding(Severity.ERROR, 'spec-status', index, number, message))
        status = status_of(spec.read_text())
        if status in STATUSES and cells[1] in STATUSES and cells[1] != status:
            message = (
                f'index Status {cells[1]!r} differs from {spec.name} status '
                f'{status!r} — format.md: Status matches the frontmatter'
            )
            findings.append(finding(Severity.ERROR, 'spec-status', index, number, message))
    return findings, linked


def check_index(root: Path, files: list[Path], repo: Path) -> list[Finding]:
    """Every spec has a row in `specs/index.md`, or in a `<phase>/index.md`
    the root index links.
    """
    index = root / 'index.md'
    if not index.is_file():
        message = (
            'missing — format.md: specs/index.md is the master table; ALWAYS add a row on create'
        )
        return [finding(Severity.ERROR, 'spec-index-row', index, 1, message)]
    specs = {path.resolve() for path in files}
    findings: list[Finding] = []
    linked: set[Path] = set()
    for each in [index, *phase_indexes(index, repo)]:
        found, rows = check_one_index(each, specs, repo)
        findings.extend(found)
        linked |= rows
    for path in files:
        if path.resolve() in linked:
            continue
        message = (
            f'no row in {index} or a phase index it links — format.md: ALWAYS add a row '
            'on create, remove the row with the file'
        )
        findings.append(finding(Severity.ERROR, 'spec-index-row', path, 1, message))
    return findings


def check_links(path: Path, text: str, repo: Path) -> list[Finding]:
    """Every link in the body resolves; a link quoted in inline code is an example."""
    findings: list[Finding] = []
    for number, line in prose(text):
        for target, named in linked_files(TICKED.sub('', line), path.parent, repo):
            if named.exists():
                continue
            message = (
                f'link {target!r} resolves to nothing — format.md self-review: a moved or '
                'renamed file takes its links with it'
            )
            findings.append(finding(Severity.ERROR, 'spec-link', path, number, message))
    return findings


def check_prose(path: Path, text: str) -> list[Finding]:
    status = status_of(text)
    findings: list[Finding] = []
    for number, line in prose(text):
        bare = TICKED.sub('', line)
        undecided = TBD.search(bare)
        if undecided is not None:
            message = (
                f'{undecided.group(0)!r} — format.md: NEVER use "TBD" / "TODO" / '
                '"implement later" — decide now or omit'
            )
            findings.append(finding(Severity.ERROR, 'spec-tbd', path, number, message))
        planned = FUTURE.search(bare)
        if planned is not None:
            message = (
                f'{planned.group(0)!r} — format.md: NEVER write future-tense plans; '
                'a spec describes the design of the change, not a schedule (warn)'
            )
            findings.append(finding(Severity.WARN, 'spec-future-tense', path, number, message))
        history = HISTORY.search(bare)
        if history is not None:
            message = (
                f'{history.group(0)!r} — format.md: a spec states what is; history lives '
                'in git (warn)'
            )
            findings.append(finding(Severity.WARN, 'spec-history', path, number, message))
        for pattern, hint in WORDING:
            word = pattern.search(bare)
            if word is not None:
                message = f'{word.group(0)!r} — format.md: {hint} (warn)'
                findings.append(finding(Severity.WARN, 'spec-wording', path, number, message))
        if OPTIONS.match(line):
            message = (
                'lays out options — format.md: state the decision and its one caveat, '
                'not the option space (warn)'
            )
            findings.append(finding(Severity.WARN, 'spec-options', path, number, message))
        if OPEN_QUESTIONS.match(line) and status not in OPEN_STATUSES:
            message = (
                f'open questions in a {status!r} spec — format.md: promotion out of draft '
                'answers them or cuts them (warn)'
            )
            findings.append(finding(Severity.WARN, 'spec-open-questions', path, number, message))
        if CHECKLIST.match(line):
            message = (
                'task-list item — format.md: no checklists or TODO items; state what is, '
                'BUGS.md holds what is not (warn)'
            )
            findings.append(finding(Severity.WARN, 'spec-checklist', path, number, message))
    return findings


def check_pointers(root: Path, path: Path, text: str) -> list[Finding]:
    repo = repo_root(root.absolute().parent)
    findings: list[Finding] = []
    named_any = False
    for number, line in prose(text):
        for token in TICKED.findall(line):
            named_any = named_any or names_file(token)
            pointer = pointer_path(token)
            if pointer is None:
                continue
            matches = resolve_pointer(pointer, path, root)
            if len(matches) > 1:
                message = (
                    f'`{token}` matches {len(matches)} files under {repo} — name the path '
                    'from the repo root (warn)'
                )
            elif not matches:
                message = (
                    f'`{token}` does not resolve under {repo} — format.md self-review: '
                    'code pointers resolve (warn)'
                )
            else:
                message = past_end(token, matches[0])
                if message is None:
                    continue
            findings.append(finding(Severity.WARN, 'spec-pointer', path, number, message))
    if status_of(text) in POINTED_STATUSES and not named_any:
        message = (
            f'a {status_of(text)} spec that names no file — format.md: keep WHY and the '
            'code pointers (warn)'
        )
        findings.append(finding(Severity.WARN, 'spec-no-pointer', path, 1, message))
    return findings


def past_end(token: str, target: Path) -> str | None:
    at = AT_LINE.search(token)
    if at is None or not target.is_file():
        return None
    lines = line_count(target)
    first = int(at.group(1))
    last = int(at.group(2) or first)
    if 1 <= first <= last <= lines:
        return None
    return f'`{token}` points past the end of the file ({lines} lines) — re-anchor it (warn)'


def check_tables(files: list[Path]) -> list[Finding]:
    """A table is declared in exactly one spec; a second declaration is a fork."""
    owners: dict[str, list[tuple[Path, int]]] = {}
    for path in files:
        for number, line in split_fences(path.read_text())[1]:
            for name in CREATE_TABLE.findall(line):
                owners.setdefault(name.lower(), []).append((path, number))
    findings: list[Finding] = []
    for name, places in owners.items():
        specs = sorted({path for path, _ in places})
        if len(specs) < 2:
            continue
        path, number = places[0]
        others = ', '.join(spec.name for spec in specs if spec != path)
        message = (
            f'table {name!r} is also declared in {others} — format.md: one owning spec, '
            'the others link to it'
        )
        findings.append(finding(Severity.ERROR, 'spec-table-owner', path, number, message))
    return findings


def check_corpus(root: Path) -> list[Finding]:
    files = spec_files(root)
    if not files and not (root / 'index.md').is_file():
        return []
    repo = repo_root(root.absolute().parent)
    findings = check_index(root, files, repo)
    findings.extend(check_numbers(files))
    findings.extend(check_tables(files))
    for path in files:
        text = path.read_text()
        findings.extend(check_naming(root, path))
        findings.extend(check_status(path, text))
        findings.extend(check_length(path, text))
        findings.extend(check_links(path, text, repo))
        findings.extend(check_prose(path, text))
        findings.extend(check_pointers(root, path, text))
    return findings


def run(paths: list[Path], verbose: bool) -> int:
    missing = [path for path in paths if not path.exists()]
    for path in missing:
        print(f'spec-lint: {path}: no such file or directory', file=sys.stderr)
    if missing:
        return 2
    roots = spec_roots(paths)
    if not roots:
        named = ', '.join(str(path) for path in paths)
        print(f'spec-lint: no spec corpus under {named}', file=sys.stderr)
        return 0
    errors = 0
    warnings = 0
    for root in roots:
        if verbose:
            print(f'checking {root}')
        for found in check_corpus(root):
            print(found.message)
            if found.severity is Severity.ERROR:
                errors += 1
            else:
                warnings += 1
    if errors or warnings:
        print(f'spec-lint: {errors} errors, {warnings} warnings')
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog='spec-lint',
        description='Lint specs/ corpora against the specs skill (format.md).',
        epilog=RULES_HELP,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        'paths',
        nargs='*',
        type=Path,
        default=[Path('specs')],
        help='specs dirs, spec files or project dirs (default: specs)',
    )
    parser.add_argument('-v', '--verbose', action='store_true', help='name each corpus checked')
    args = parser.parse_args()
    return run(args.paths, args.verbose)


if __name__ == '__main__':
    raise SystemExit(main())
