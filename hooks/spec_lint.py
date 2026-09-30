#!/usr/bin/env python3
"""Lint a `specs/` corpus against the `specs` skill (`skills/specs/format.md`).

The rules are format.md's self-review checklist, mechanically. Each rule names
itself and points back at format.md so a failure teaches. Errors block
(exit 2); warnings only print (English tense and path-shaped backticks are
guesses — a false hard-fail trains `--no-verify`).

Checklist item 3, "No HOW (implementation steps)", has no rule on purpose: it
is a judgement call, and a lint that guesses at it is wrong loudly.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from skill_frontmatter_lint import Finding
from skill_frontmatter_lint import Severity
from skill_frontmatter_lint import frontmatter
from skill_frontmatter_lint import parse_meta

# format.md: four lifecycle values, `experiment` beside them, and `reference`
# for docs with no lifecycle. A closed set; the index Status column uses the
# same words.
STATUSES = ('draft', 'experiment', 'planned', 'partial', 'shipped', 'reference')
# specs/<NN>-<topic>.md flat; specs/<phase>/<N>-<topic>.md under a phase dir.
NUMBERED = re.compile(r'^(\d+)-[a-z0-9]+(?:-[a-z0-9]+)*\.md$')
FLAT_PAD = 2
PHASE_DEPTH = 2
LINK = re.compile(r'\[[^\]]*\]\(([^)\s]+)\)')
TBD = re.compile(r'\bTBD\b|\bTODO\b|implement later', re.IGNORECASE)
FUTURE = re.compile(r"\bwe will\b|\bwe'll\b|\bwill be\b", re.IGNORECASE)
TICKED = re.compile(r'`([^`\n]+)`')
AT_LINE = re.compile(r':\d+(?:-\d+)?$')
SUFFIX = re.compile(r'\.[a-z][a-z0-9+]{0,9}$')
NOT_IN_PATH = frozenset(' \t*?{}<>$|"\'()[]=,;!`')
SKIP_DIRS = frozenset({'.git', 'node_modules', '.venv', '__pycache__', 'dist', 'build'})


def nearest_root(path: Path) -> Path | None:
    for candidate in (path, *path.parents):
        if candidate.name == 'specs' and candidate.is_dir():
            return candidate
    return None


def discovered(root: Path) -> list[Path]:
    """Dirs named specs that hold a spec corpus.

    A test suite in `e2e/specs/` is also a directory named specs; requiring an
    index or one numbered file keeps discovery off it.
    """
    found: list[Path] = []
    for path in root.glob('**/specs'):
        if not path.is_dir() or SKIP_DIRS & set(path.parts):
            continue
        numbered = any(NUMBERED.match(child.name) for child in path.glob('*.md'))
        if (path / 'index.md').is_file() or numbered:
            found.append(path)
    return found


def spec_roots(paths: list[Path]) -> list[Path]:
    roots: list[Path] = []
    for path in paths:
        target = path.parent if path.is_file() else path
        named = nearest_root(target)
        if named is not None:
            roots.append(named)
            continue
        if (target / 'specs').is_dir():
            roots.append(target / 'specs')
        roots.extend(discovered(target))
    return sorted(set(roots))


def spec_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.glob('**/*.md')
        if path.name != 'index.md' and not SKIP_DIRS & set(path.parts)
    )


def prose(text: str) -> list[tuple[int, str]]:
    """Numbered lines outside fenced blocks — a fence quotes code, not spec prose."""
    lines: list[tuple[int, str]] = []
    fenced = False
    for number, line in enumerate(text.splitlines(), start=1):
        if line.lstrip().startswith(('```', '~~~')):
            fenced = not fenced
            continue
        if not fenced:
            lines.append((number, line))
    return lines


def row_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith('|') or not stripped.endswith('|'):
        return []
    return [cell.strip() for cell in stripped[1:-1].split('|')]


def pointer_path(token: str) -> str | None:
    """The repo-relative path a backticked token points at, or None.

    A pointer is `path:line` or a backticked path with a slash — a bare
    `config.yaml` reads as a kind of file more often than a place in this repo.
    An extension is lowercase, which keeps `net/http.Server` out.
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
    return path


# --- rules (format.md self-review) ----------------------------------------


def check_naming(root: Path, path: Path) -> list[Finding]:
    parts = path.relative_to(root).parts
    shape = 'format.md: specs/<NN>-<topic>.md flat, or specs/<phase>/<N>-<topic>.md'
    if len(parts) > PHASE_DEPTH:
        return [
            Finding(
                Severity.ERROR,
                'spec-naming',
                f'{path}:1: [spec-naming] {len(parts) - 1} directories below specs/ — {shape}',
            )
        ]
    match = NUMBERED.match(parts[-1])
    if match is None:
        return [
            Finding(
                Severity.ERROR,
                'spec-naming',
                f'{path}:1: [spec-naming] name {parts[-1]!r} is not <number>-<kebab-topic>.md '
                '— format.md: NEVER use an unnumbered by-content name',
            )
        ]
    if len(parts) == 1 and len(match.group(1)) < FLAT_PAD:
        return [
            Finding(
                Severity.WARN,
                'spec-naming',
                f'{path}:1: [spec-naming] flat number {match.group(1)!r} is not zero-padded '
                '— format.md: NN a zero-padded integer, the first is 01 (warn)',
            )
        ]
    return []


def check_status(path: Path, text: str) -> list[Finding]:
    split = frontmatter(text)
    if split is None:
        return [
            Finding(
                Severity.ERROR,
                'spec-status',
                f'{path}:1: [spec-status] no YAML frontmatter — format.md: every spec file '
                'starts with `status:`',
            )
        ]
    meta = parse_meta(split[0])
    value = str(meta.get('status', '')).strip() if meta else ''
    if value in STATUSES:
        return []
    return [
        Finding(
            Severity.ERROR,
            'spec-status',
            f'{path}:1: [spec-status] status {value!r} is not one of '
            f'{", ".join(STATUSES)} — format.md defines the complete set',
        )
    ]


def check_index(root: Path, files: list[Path]) -> list[Finding]:
    index = root / 'index.md'
    if not index.is_file():
        return [
            Finding(
                Severity.ERROR,
                'spec-index-row',
                f'{index}:1: [spec-index-row] missing — format.md: specs/index.md is the '
                'master table; ALWAYS add a row on create',
            )
        ]
    findings: list[Finding] = []
    linked: set[Path] = set()
    for number, line in prose(index.read_text()):
        for target in LINK.findall(line):
            if '://' in target or target.startswith('#'):
                continue
            resolved = root / target.split('#')[0]
            if not resolved.exists():
                findings.append(
                    Finding(
                        Severity.ERROR,
                        'spec-index-dangling',
                        f'{index}:{number}: [spec-index-dangling] link {target!r} resolves to '
                        'nothing — format.md: index.md is the master table of the files present',
                    )
                )
                continue
            linked.add(resolved.resolve())
        cells = row_cells(line)
        if len(cells) > 1 and LINK.search(cells[0]) and cells[1] not in STATUSES:
            findings.append(
                Finding(
                    Severity.ERROR,
                    'spec-status',
                    f'{index}:{number}: [spec-status] index Status cell {cells[1]!r} is not one '
                    f'of {", ".join(STATUSES)} — format.md: the Status column carries the '
                    'lifecycle value, not prose',
                )
            )
    findings.extend(
        Finding(
            Severity.ERROR,
            'spec-index-row',
            f'{path}:1: [spec-index-row] no row in {index} — format.md: ALWAYS add a row '
            'on create, update Status on ship',
        )
        for path in files
        if path.resolve() not in linked
    )
    return findings


def check_prose(path: Path, text: str) -> list[Finding]:
    findings: list[Finding] = []
    for number, line in prose(text):
        undecided = TBD.search(line)
        if undecided is not None:
            findings.append(
                Finding(
                    Severity.ERROR,
                    'spec-tbd',
                    f'{path}:{number}: [spec-tbd] {undecided.group(0)!r} — format.md: NEVER use '
                    '"TBD" / "TODO" / "implement later" — decide now or omit',
                )
            )
        planned = FUTURE.search(line)
        if planned is not None:
            findings.append(
                Finding(
                    Severity.WARN,
                    'spec-future-tense',
                    f'{path}:{number}: [spec-future-tense] {planned.group(0)!r} — format.md: '
                    'NEVER write future-tense plans; specs describe state, not work (warn)',
                )
            )
    return findings


def check_pointers(root: Path, path: Path, text: str) -> list[Finding]:
    bases = (root.parent, path.parent, root)
    findings: list[Finding] = []
    for number, line in prose(text):
        for token in TICKED.findall(line):
            pointer = pointer_path(token)
            if pointer is None or any((base / pointer).exists() for base in bases):
                continue
            findings.append(
                Finding(
                    Severity.WARN,
                    'spec-pointer',
                    f'{path}:{number}: [spec-pointer] `{token}` does not resolve under '
                    f'{root.parent} — format.md self-review: code pointers resolve (warn)',
                )
            )
    return findings


def check_corpus(root: Path) -> list[Finding]:
    files = spec_files(root)
    if not files and not (root / 'index.md').is_file():
        return []
    findings = check_index(root, files)
    for path in files:
        text = path.read_text()
        findings.extend(check_naming(root, path))
        findings.extend(check_status(path, text))
        findings.extend(check_prose(path, text))
        findings.extend(check_pointers(root, path, text))
    return findings


def report(root: Path) -> int:
    status = 0
    for finding in check_corpus(root):
        print(finding.message, file=sys.stderr)
        if finding.severity is Severity.ERROR:
            status = 2
    return status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+', type=Path)
    args = parser.parse_args()

    status = 0
    for root in spec_roots(args.paths):
        status = max(status, report(root))
    return status


if __name__ == '__main__':
    raise SystemExit(main())
