#!/usr/bin/env python3

import argparse
import functools
import os
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import cast
from urllib.parse import unquote

from markdown_it import MarkdownIt
from markdown_it.rules_inline import backtick
from markdown_it.rules_inline.state_inline import StateInline
from markdown_it.tree import SyntaxTreeNode


def is_code_span(state: StateInline, silent: bool) -> bool:
    start = state.pos
    count = len(state.tokens)
    matched = backtick(state, silent)
    if len(state.tokens) > count and state.tokens[-1].type == 'code_inline':
        state.tokens[-1].meta['line'] = state.src.count('\n', 0, start)
    return matched


MARKDOWN = MarkdownIt('commonmark').enable('table')
MARKDOWN.inline.ruler.at('backticks', is_code_span)
STATUSES = ('draft', 'experiment', 'planned', 'partial', 'shipped', 'reference')
NUMBERED = re.compile(r'^(\d+)-[a-z0-9]+(?:-[a-z0-9]+)*\.md$')
NOT_SPECS = frozenset({'index.md', 'CLAUDE.md', 'AGENTS.md'})
FLAT_PAD = 2
PHASE_DEPTH = 2
BOUNDARY = re.compile(r'^---\s*$', re.MULTILINE)
STATUS = re.compile(r"""status: +(?:([a-z]+)|'([a-z]+)'|"([a-z]+)")(?: +#.*)? *""")
SCHEME = re.compile(r'^[a-z][a-z0-9+.-]*:')
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
spec file, including phase directories. No corpus is a clean empty project.

rules (implementation completion requires tests and review):
  spec-naming          <NN>-<topic>.md flat or <phase>/<N>-<topic>.md   error
                       two files share a number                         error
                       flat number not zero-padded                     warn
  spec-status          malformed or missing status frontmatter         error
                       status outside the closed vocabulary
                       index Status cell is prose or differs from the   error
                       file
  spec-index-row       missing or duplicate spec row in active indexes error
  spec-index-dangling  index names an absent spec or phase index        error
  spec-pointer         `dir/path` or `path:line` stale, ambiguous or    warn
                       past the end of the file

exit codes: 0 no errors, 1 errors found, 2 bad input or arguments
Markdown syntax, formatting and links belong to rumdl.
"""


class Severity(Enum):
    ERROR = 'error'
    WARN = 'warn'


@dataclass(frozen=True)
class Finding:
    severity: Severity
    rule: str
    message: str


class Arguments(argparse.Namespace):
    paths: list[Path]
    verbose: bool


def finding(severity: Severity, rule: str, where: Path, line: int, text: str) -> Finding:
    return Finding(severity, rule, f'{where}:{line}: [{rule}] {text}')


def is_spec_corpus(path: Path) -> bool:
    return any(
        name == 'index.md' or NUMBERED.fullmatch(name) for _, names in walk(path) for name in names
    )


def is_skipped_dir(path: Path) -> bool:
    if path.name in SKIP_DIRS:
        return True
    return (path / '.git').exists()


def walk_error(error: OSError) -> None:
    raise error


def walk(top: Path) -> list[tuple[Path, list[str]]]:
    found: list[tuple[Path, list[str]]] = []
    for dirpath, dirnames, filenames in os.walk(top, onerror=walk_error):
        here = Path(dirpath)
        dirnames[:] = [d for d in dirnames if not is_skipped_dir(here / d)]
        found.append((here, filenames))
    return found


def nearest_root(path: Path) -> Path | None:
    for candidate in (path, *path.parents):
        if candidate.name == 'specs' and is_spec_corpus(candidate):
            return candidate
    return None


def discovered(root: Path) -> list[Path]:
    return [here for here, _ in walk(root) if here.name == 'specs' and is_spec_corpus(here)]


def spec_roots(paths: list[Path]) -> list[Path]:
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
    return sorted(
        here / name
        for here, names in walk(root)
        for name in names
        if name.endswith('.md') and name not in NOT_SPECS
    )


def status_of(text: str) -> str | None:
    if not text.startswith('---\n'):
        return None
    match = BOUNDARY.search(text, 4)
    if match is None:
        return None
    lines = [
        line
        for line in text[4 : match.start()].splitlines()
        if line.strip() and not line.startswith('#')
    ]
    if len(lines) != 1:
        return ''
    match = STATUS.fullmatch(lines[0])
    return next(group for group in match.groups() if group) if match else ''


def link_target(target: str) -> str | None:
    if '://' in target or target.startswith('#') or SCHEME.match(target):
        return None
    if set(target) & set('<>{}$'):
        return None
    return unquote(target.split('#', maxsplit=1)[0])


def link_file(named: str, beside: Path, repo: Path) -> Path:
    return repo / named.lstrip('/') if named.startswith('/') else beside / named


def pointer_path(token: str) -> str | None:
    if NOT_IN_PATH & set(token) or '://' in token or '..' in token:
        return None
    if token.startswith(('/', '~', '-', '#', '@', ':')) or token.endswith('/'):
        return None
    path = AT_LINE.sub('', token)
    if '/' not in path and (path == token or SUFFIX.search(path) is None):
        return None
    if PLACEHOLDER.search(path):
        return None
    return path


def repo_root(component: Path) -> Path:
    for candidate in (component, *component.parents):
        if (candidate / '.git').exists():
            return candidate
    return component


@functools.cache
def indexed_files(repo: Path) -> dict[str, list[Path]]:
    by_name: dict[str, list[Path]] = {}
    for here, filenames in walk(repo):
        for name in filenames:
            by_name.setdefault(name, []).append((here / name).relative_to(repo))
    return by_name


@functools.cache
def line_count(path: Path) -> int:
    return len(path.read_bytes().splitlines())


def resolve_pointer(pointer: str, spec: Path, root: Path) -> list[Path]:
    spec = spec.absolute()
    root = root.absolute()
    component = root.parent
    repo = repo_root(component)
    bases = [spec.parent, root, component]
    while bases[-1] != repo:
        bases.append(bases[-1].parent)
    for base in bases:
        if (base / pointer).is_file():
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
        f'invalid status header {status!r}; expected one status: line with '
        f'one of {", ".join(STATUSES)}'
    )
    return [finding(Severity.ERROR, 'spec-status', path, 1, message)]


def linked_files(node: SyntaxTreeNode, beside: Path, repo: Path) -> list[tuple[str, Path]]:
    found: list[tuple[str, Path]] = []
    for child in node.walk():
        if child.type != 'link':
            continue
        target = child.attrGet('href')
        if not isinstance(target, str):
            continue
        named = link_target(target)
        if named is not None:
            found.append((target, link_file(named, beside, repo)))
    return found


def phase_indexes(index: Path, repo: Path) -> list[Path]:
    found: list[Path] = []
    tree = SyntaxTreeNode(MARKDOWN.parse(index.read_text(encoding='utf-8-sig')))
    for _, path in linked_files(tree, index.parent, repo):
        candidate = path.resolve()
        if (
            candidate.name == 'index.md'
            and candidate.is_file()
            and candidate.parent.parent == index.parent.resolve()
        ):
            found.append(candidate)
    return sorted(set(found))


def check_one_index(
    index: Path, specs: set[Path], root: Path, repo: Path
) -> tuple[list[Finding], list[Path]]:
    findings: list[Finding] = []
    linked: list[Path] = []
    tree = SyntaxTreeNode(MARKDOWN.parse(index.read_text(encoding='utf-8-sig')))
    for node in tree.walk(include_self=False):
        if node.type != 'inline' or node.map is None:
            continue
        number = node.map[0] + 1
        for target, path in linked_files(node, index.parent, repo):
            named = path.resolve()
            if (
                named.is_relative_to(root.resolve())
                and named.suffix == '.md'
                and not named.is_file()
            ):
                message = (
                    f'link {target!r} resolves to nothing — format.md: index.md is the '
                    'master table of the files present'
                )
                findings.append(
                    finding(Severity.ERROR, 'spec-index-dangling', index, number, message)
                )
    for node in tree.walk(include_self=False):
        if node.type != 'tr' or node.map is None or len(node.children) < 3:
            continue
        number = node.map[0] + 1
        cells = [cell.children[0] for cell in node.children]
        rows = [named.resolve() for _, named in linked_files(cells[0], index.parent, repo)]
        spec = next((row for row in rows if row in specs), None)
        if spec is None:
            continue
        if len(rows) != 1:
            message = 'the Spec cell must name exactly one spec'
            findings.append(finding(Severity.ERROR, 'spec-index-row', index, number, message))
            continue
        linked.append(spec)
        cell_status = cells[1].content
        if cell_status not in STATUSES:
            message = (
                f'index Status cell {cell_status!r} is not one of {", ".join(STATUSES)} '
                '— format.md: the Status column carries the lifecycle value, not prose'
            )
            findings.append(finding(Severity.ERROR, 'spec-status', index, number, message))
        status = status_of(spec.read_text(encoding='utf-8-sig'))
        if status in STATUSES and cell_status in STATUSES and cell_status != status:
            message = (
                f'index Status {cell_status!r} differs from {spec.name} status '
                f'{status!r} — format.md: Status matches the frontmatter'
            )
            findings.append(finding(Severity.ERROR, 'spec-status', index, number, message))
    return findings, linked


def check_index(root: Path, files: list[Path], repo: Path) -> list[Finding]:
    index = root / 'index.md'
    if not index.is_file():
        message = (
            'missing — format.md: specs/index.md is the master table; ALWAYS add a row on create'
        )
        return [finding(Severity.ERROR, 'spec-index-row', index, 1, message)]
    specs = {path.resolve() for path in files}
    findings: list[Finding] = []
    linked: list[Path] = []
    active = {index.resolve(), *phase_indexes(index, repo)}
    indexes = sorted(here / 'index.md' for here, names in walk(root) if 'index.md' in names)
    for each in indexes:
        found, rows = check_one_index(each, specs, root, repo)
        findings.extend(found)
        if each.resolve() in active:
            linked.extend(rows)
    for path in files:
        count = linked.count(path.resolve())
        if count == 1:
            continue
        if count > 1:
            message = f'{count} index rows — each spec needs exactly one row'
            findings.append(finding(Severity.ERROR, 'spec-index-row', path, 1, message))
            continue
        message = (
            f'no row in {index} or a phase index it links — format.md: ALWAYS add a row '
            'on create, remove the row with the file'
        )
        findings.append(finding(Severity.ERROR, 'spec-index-row', path, 1, message))
    return findings


def check_pointers(root: Path, path: Path, text: str) -> list[Finding]:
    repo = repo_root(root.absolute().parent)
    findings: list[Finding] = []
    for block in MARKDOWN.parse(text):
        if block.type != 'inline' or block.map is None or block.children is None:
            continue
        for child in block.children:
            if child.type != 'code_inline':
                continue
            token = child.content
            number = block.map[0] + cast(int, child.meta['line']) + 1
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


def check_corpus(root: Path) -> list[Finding]:
    files = spec_files(root)
    has_index = any('index.md' in names for _, names in walk(root))
    if not files and not has_index:
        return []
    repo = repo_root(root.absolute().parent)
    findings = check_index(root, files, repo)
    findings.extend(check_numbers(files))
    for path in files:
        text = path.read_text(encoding='utf-8-sig')
        findings.extend(check_naming(root, path))
        findings.extend(check_status(path, text))
        findings.extend(check_pointers(root, path, text))
    return findings


def run(paths: list[Path], verbose: bool) -> int:
    indexed_files.cache_clear()
    line_count.cache_clear()
    try:
        missing = [path for path in paths if not path.exists()]
        for path in missing:
            print(f'speclint: {path}: no such file or directory', file=sys.stderr)
        if missing:
            return 2
        roots = spec_roots(paths)
        if not roots:
            named = ', '.join(str(path) for path in paths)
            print(f'speclint: no spec corpus under {named}', file=sys.stderr)
            return 2 if any(not path.is_dir() for path in paths) else 0
    except (OSError, ValueError) as err:
        print(f'speclint: Cannot discover corpora: {err}', file=sys.stderr)
        return 2
    errors = 0
    warnings = 0
    for root in roots:
        if verbose:
            print(f'checking {root}')
        try:
            findings = check_corpus(root)
        except (OSError, ValueError) as err:
            print(f'speclint: Cannot read corpus {root}: {err}', file=sys.stderr)
            return 2
        for found in findings:
            print(found.message)
            if found.severity is Severity.ERROR:
                errors += 1
            else:
                warnings += 1
    if errors or warnings:
        print(f'speclint: {errors} errors, {warnings} warnings')
    return 1 if errors else 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog='speclint',
        description='Check spec naming, status, indexes and code pointers.',
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
    args = Arguments()
    parser.parse_args(namespace=args)
    if sys.__stdout__ is not None:
        sys.__stdout__.reconfigure(errors='backslashreplace')
    if sys.__stderr__ is not None:
        sys.__stderr__.reconfigure(errors='backslashreplace')
    return run(args.paths, args.verbose)


if __name__ == '__main__':
    raise SystemExit(main())
