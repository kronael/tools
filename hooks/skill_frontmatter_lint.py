#!/usr/bin/env python3
"""Lint SKILL.md: frontmatter YAML (autofix) plus wisdom-skill body rules, and
scan every .md under the paths given for leaked home paths and secrets.

Body rules are sourced verbatim from the `wisdom` skill (the skill-authoring
spec). Each rule names itself and points back at wisdom so a failure teaches.
Errors block (exit 2); warnings only print (length and disambiguation are
fuzzy — a false hard-fail trains `--no-verify`).
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import Counter
from dataclasses import dataclass
from enum import Enum
from fnmatch import fnmatch
from pathlib import Path

import yaml

BOUNDARY = re.compile(r'^---\s*$', re.MULTILINE)
FIX_FIELDS = {'description', 'when_to_use'}

REQUIRED_KEYS = ('name', 'description', 'when_to_use')
# Keys Claude Code reads (code.claude.com/docs/en/skills). Anything else is
# ignored locally but rejected by other Agent Skills consumers, so it is an
# error here. Free-form provenance belongs under `metadata`.
KNOWN_KEYS = {
    'name',
    'description',
    'when_to_use',
    'argument-hint',
    'arguments',
    'disable-model-invocation',
    'user-invocable',
    'allowed-tools',
    'disallowed-tools',
    'model',
    'effort',
    'context',
    'agent',
    'background',
    'shell',
    'paths',
    'hooks',
    'metadata',
    'license',
    'compatibility',
}
SHOULD = re.compile(r'\bSHOULD\b')
DEFAULT_MAX_LINES = 200
# Workflow/runbook skills carry procedure and legitimately run long (wisdom
# tiered length). Keyed on the skill's directory name.
LONG_MAX_LINES = 500
LONG_SKILLS = frozenset({'ship'})
# Claude Code lists each skill as "<description> - <when_to_use>" and cuts that
# text at this many characters (its skillListingMaxDescChars default); a
# keyword past the cap never reaches the model.
LISTING_CAP = 1536
# Claude Code preloads SKILL.md and loads a directory's CLAUDE.md on its own.
# Every other sibling is cold until a chain of names reaches it.
PRELOADED = frozenset({'SKILL.md', 'CLAUDE.md'})
# A home path naming a real account leaks the authoring machine. A one-character
# account segment is this bundle's placeholder for an illustrative path
# (`/home/u/app/x` teaches the project-slug transform), so it stays. So do
# `/home/dockbox` and `/home/claude`: the HOME of this repo's own container
# user (dockbox/README.md, CHANGELOG.md), which names no authoring machine.
LOCAL_PATH = re.compile(r'/(?:home|Users)/(?!(?:dockbox|claude)\b)[A-Za-z0-9._-]{2,}')
SECRET = re.compile(
    r'sk-ant-[\w-]{8,}|ghp_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|BEGIN [A-Z ]*PRIVATE KEY'
)
# CLAUDE.md bans org-specific refs too. Nothing here checks them: a pattern
# would have to name the org, which is the ref it exists to keep out.
# A file whose point is a real-looking path (what to strip, where a slug comes
# from) opts out of the path rule with this marker. Secrets have no opt-out.
ALLOW_LOCAL_PATH = '<!-- lint: allow skill-local-path -->'


class Severity(Enum):
    ERROR = 'error'
    WARN = 'warn'


@dataclass(frozen=True)
class Finding:
    severity: Severity
    rule: str
    message: str


def visible_files(root: Path, pattern: str) -> list[Path]:
    """Files under `root` matching `pattern`, skipping hidden directories: they
    hold ignored state such as `.claude/plans/` and the `.git` store, not source.
    """
    found: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        found.extend(Path(dirpath) / name for name in filenames if fnmatch(name, pattern))
    return found


def skill_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.name == 'SKILL.md':
            files.append(path)
        elif path.is_dir():
            files.extend(visible_files(path, 'SKILL.md'))
    return sorted(set(files))


def leak_docs(paths: list[Path]) -> list[Path]:
    docs: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == '.md':
            docs.append(path)
        elif path.is_dir():
            docs.extend(visible_files(path, '*.md'))
    return sorted(set(docs))


def frontmatter(text: str) -> tuple[str, str] | None:
    if not text.startswith('---\n'):
        return None
    match = BOUNDARY.search(text, 4)
    if match is None:
        return None
    return text[4 : match.start()], text[match.end() :].lstrip('\n')


def yaml_error(text: str) -> str | None:
    try:
        yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return str(exc).splitlines()[0]
    return None


def parse_meta(text: str) -> dict | None:
    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    return data if isinstance(data, dict) else None


def fix_value(key: str, value: str) -> str:
    value = value.strip()
    if not value or value[0] in '[{>|':
        return value
    if key == 'when_to_use':
        try:
            parts = next(csv.reader([value], skipinitialspace=True))
            value = ', '.join(x.strip() for x in parts if x.strip())
        except csv.Error:
            pass
    return json.dumps(value, ensure_ascii=False)


def fix_frontmatter(text: str) -> str:
    lines: list[str] = []
    for raw in text.splitlines():
        key, sep, value = raw.partition(':')
        fixed = f'{key}: {fix_value(key, value)}' if sep and key in FIX_FIELDS else raw
        lines.append(fixed)
    return '\n'.join(lines).rstrip() + '\n'


def check_keys(path: Path, meta: dict | None) -> list[Finding]:
    if meta is None:
        return []  # unparseable YAML — the frontmatter check owns that failure
    findings: list[Finding] = []
    missing = [key for key in REQUIRED_KEYS if not str(meta.get(key, '')).strip()]
    if missing:
        findings.append(
            Finding(
                Severity.ERROR,
                'skill-keys',
                f'{path}:1: [skill-keys] missing frontmatter key(s): {", ".join(missing)} '
                '— wisdom: name, description, when_to_use are required',
            )
        )
    unknown = sorted(set(meta) - KNOWN_KEYS)
    if unknown:
        findings.append(
            Finding(
                Severity.ERROR,
                'skill-keys',
                f'{path}:1: [skill-keys] unrecognised frontmatter key(s): {", ".join(unknown)} '
                '— wisdom: NEVER invent a key; provenance goes under `metadata`',
            )
        )
    return findings


def check_name(path: Path, meta: dict | None) -> list[Finding]:
    if meta is None:
        return []
    name = meta.get('name')
    if name is None or name == path.parent.name:
        return []
    return [
        Finding(
            Severity.ERROR,
            'skill-name',
            f'{path}:1: [skill-name] name {name!r} does not match directory '
            f'{path.parent.name!r} — wisdom: the directory name IS the skill name',
        )
    ]


def check_notfor(path: Path, meta: dict | None) -> list[Finding]:
    if meta is None:
        return []
    if 'NOT for' in str(meta.get('description', '')):
        return []
    return [
        Finding(
            Severity.WARN,
            'skill-notfor',
            f'{path}:1: [skill-notfor] description has no "NOT for <case> (use <skill>)" '
            'clause — wisdom: ALWAYS add it to disambiguate neighbors (warn)',
        )
    ]


def listing_text(meta: dict) -> str:
    description = str(meta.get('description', '') or '')
    when = meta.get('when_to_use', '') or ''
    if isinstance(when, list):
        when = ', '.join(str(item) for item in when)
    return f'{description} - {when}' if when else description


def check_budget(path: Path, meta: dict | None) -> list[Finding]:
    if meta is None:
        return []
    length = len(listing_text(meta))
    if length <= LISTING_CAP:
        return []
    return [
        Finding(
            Severity.WARN,
            'skill-budget',
            f'{path}:1: [skill-budget] description + when_to_use is {length} chars '
            f'(> {LISTING_CAP}) — wisdom: the listing cuts the rest, keywords past the cap '
            'never route (warn)',
        )
    ]


def check_should(path: Path, body: str, body_line0: int) -> list[Finding]:
    findings: list[Finding] = []
    for offset, line in enumerate(body.splitlines()):
        if SHOULD.search(line):
            findings.append(
                Finding(
                    Severity.ERROR,
                    'skill-should',
                    f'{path}:{body_line0 + offset}: [skill-should] body uses the directive '
                    'SHOULD — wisdom: NEVER use SHOULD (too soft); ALWAYS/NEVER only',
                )
            )
    return findings


def check_length(path: Path, body: str) -> list[Finding]:
    lines = len(body.splitlines())
    cap = LONG_MAX_LINES if path.parent.name in LONG_SKILLS else DEFAULT_MAX_LINES
    if lines <= cap:
        return []
    return [
        Finding(
            Severity.WARN,
            'skill-length',
            f'{path}: [skill-length] body is {lines} lines (> {cap}) '
            '— wisdom: ALWAYS keep under 200 lines; push overflow to sibling files (warn)',
        )
    ]


def check_router(path: Path) -> list[Finding]:
    for ancestor in path.parent.parents:
        if (ancestor / 'SKILL.md').is_file():
            return [
                Finding(
                    Severity.WARN,
                    'skill-router',
                    f'{path}: [skill-router] nested under {ancestor / "SKILL.md"} — wisdom: '
                    'NEVER name a data file SKILL.md (it preloads); rename it (warn)',
                )
            ]
        if (ancestor / '.git').exists():
            break
    return []


def sibling_docs(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob('*.md') if p.name not in PRELOADED}


def suffixes(rel: str) -> list[str]:
    parts = Path(rel).parts
    return ['/'.join(parts[i:]) for i in range(len(parts))]


def name_forms(docs: set[str]) -> dict[str, set[str]]:
    """Forms that name each doc: its path from the skill root, plus every
    shorter path suffix no other doc under the skill shares. A bare basename
    therefore counts only while it is unique; once two files share one, each
    needs a directory in front of it.
    """
    counts = Counter(form for rel in docs for form in suffixes(rel))
    return {rel: {rel, *(form for form in suffixes(rel) if counts[form] == 1)} for rel in docs}


def names_doc(forms: set[str]) -> re.Pattern[str]:
    """Match any of `forms` at a filename boundary.

    The lookbehind stops `contexts.md` from counting as a reference to `ts.md` —
    a bare substring test reports a reached file that nothing names. It allows a
    leading `/` so that `render/flavors/remotion.md`, written from an
    intermediate file, still names `remotion.md`.
    """
    return re.compile(rf'(?<![\w.-])(?:{"|".join(re.escape(form) for form in sorted(forms))})')


def check_reachable(path: Path) -> list[Finding]:
    root = path.parent
    pending = sibling_docs(root)
    forms = name_forms(pending)
    frontier = [path]
    while frontier and pending:
        text = frontier.pop().read_text()
        for rel in sorted(pending):
            if names_doc(forms[rel]).search(text):
                pending.discard(rel)
                frontier.append(root / rel)
    return [
        Finding(
            Severity.ERROR,
            'skill-orphan',
            f'{root / rel}: [skill-orphan] no chain of names from SKILL.md reaches it '
            '— wisdom: only SKILL.md preloads, so an unnamed sibling is dead weight; '
            'add a dispatch row (a path, when another file shares the basename) or '
            'delete the file',
        )
        for rel in sorted(pending)
    ]


def check_leaks(doc: Path) -> list[Finding]:
    text = doc.read_text()
    rules = [('skill-secret', SECRET, 'a credential shape')]
    if ALLOW_LOCAL_PATH not in text:
        rules.append(
            (
                'skill-local-path',
                LOCAL_PATH,
                'an absolute home path (an illustrative one takes a one-character '
                f'account, or the file opts out with {ALLOW_LOCAL_PATH})',
            )
        )
    findings: list[Finding] = []
    for offset, line in enumerate(text.splitlines(), start=1):
        for rule, pattern, why in rules:
            if pattern.search(line):
                findings.append(
                    Finding(
                        Severity.ERROR,
                        rule,
                        f'{doc}:{offset}: [{rule}] {why} — CLAUDE.md: NEVER ship local '
                        'paths or secrets; they belong in ~/.claude/LOCAL.md',
                    )
                )
    return findings


def check_body(path: Path, text: str, meta: dict | None, body: str) -> list[Finding]:
    body_line0 = text.count('\n', 0, text.rindex(body)) + 1 if body else 1
    return [
        *check_keys(path, meta),
        *check_name(path, meta),
        *check_notfor(path, meta),
        *check_budget(path, meta),
        *check_should(path, body, body_line0),
        *check_length(path, body),
        *check_router(path),
        *check_reachable(path),
    ]


def process(path: Path, write: bool) -> int:
    text = path.read_text()
    split = frontmatter(text)
    if split is None:
        print(f'{path}: missing frontmatter', file=sys.stderr)
        return 2

    meta, body = split
    status = 0
    error = yaml_error(meta)
    if error is not None and write:
        fixed = fix_frontmatter(meta)
        if yaml_error(fixed) is not None:
            print(f'{path}: still invalid after fix: {error}', file=sys.stderr)
            return 2
        text = f'---\n{fixed}---\n\n{body}'
        path.write_text(text)
        print(f'fixed: {path}')
        meta, status = fixed, 1
    elif error is not None:
        print(f'needs fix: {path} ({error})')
        status = 1

    # A repaired file still has to conform; fixing the YAML says nothing about
    # the name, the keys or the listing budget.
    for finding in check_body(path, text, parse_meta(meta), body):
        print(finding.message, file=sys.stderr)
        if finding.severity is Severity.ERROR:
            status = max(status, 2)
    return status


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+', type=Path)
    parser.add_argument('--write', action='store_true')
    parser.add_argument('--fail-on-write', action='store_true')
    args = parser.parse_args()

    status = 0
    for path in skill_files(args.paths):
        result = process(path, args.write)
        if result == 1 and args.write and not args.fail_on_write:
            result = 0
        status = max(status, result)
    for doc in leak_docs(args.paths):
        for finding in check_leaks(doc):
            print(finding.message, file=sys.stderr)
            status = max(status, 2)
    return status


if __name__ == '__main__':
    raise SystemExit(main())
