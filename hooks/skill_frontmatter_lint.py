#!/usr/bin/env python3
"""Lint SKILL.md: frontmatter YAML (autofix) plus wisdom-skill body rules.

Body rules are sourced verbatim from the `wisdom` skill (the skill-authoring
spec). Each rule names itself and points back at wisdom so a failure teaches.
Errors block (exit 2); warnings only print (length and disambiguation are
fuzzy — a false hard-fail trains `--no-verify`).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import yaml

BOUNDARY = re.compile(r'^---\s*$', re.MULTILINE)
FIX_FIELDS = {'description', 'when_to_use'}

REQUIRED_KEYS = ('name', 'description', 'when_to_use')
SHOULD = re.compile(r'\bSHOULD\b')
DEFAULT_MAX_LINES = 200
# Workflow/runbook skills carry procedure and legitimately run long (wisdom
# tiered length). Keyed on the skill's directory name.
LONG_MAX_LINES = 500
LONG_SKILLS = frozenset({'install', 'ship'})
# Claude Code lists each skill as "<description> - <when_to_use>" and cuts that
# text at this many characters (its skillListingMaxDescChars default); a
# keyword past the cap never reaches the model.
LISTING_CAP = 1536


class Severity(Enum):
    ERROR = 'error'
    WARN = 'warn'


@dataclass(frozen=True)
class Finding:
    severity: Severity
    rule: str
    message: str


def skill_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.name == 'SKILL.md':
            files.append(path)
        elif path.is_dir():
            files.extend(path.glob('**/SKILL.md'))
    return sorted(set(files))


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


# --- body checks (wisdom rules) -------------------------------------------


def check_keys(path: Path, meta: dict | None) -> list[Finding]:
    if meta is None:
        return []  # unparseable YAML — the frontmatter check owns that failure
    missing = [key for key in REQUIRED_KEYS if not str(meta.get(key, '')).strip()]
    if not missing:
        return []
    return [
        Finding(
            Severity.ERROR,
            'skill-keys',
            f'{path}:1: [skill-keys] missing frontmatter key(s): {", ".join(missing)} '
            '— wisdom: name, description, when_to_use are required',
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


def check_body(path: Path, text: str, meta: dict | None, body: str) -> list[Finding]:
    body_line0 = text.count('\n', 0, text.rindex(body)) + 1 if body else 1
    return [
        *check_keys(path, meta),
        *check_notfor(path, meta),
        *check_budget(path, meta),
        *check_should(path, body, body_line0),
        *check_length(path, body),
        *check_router(path),
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
    return status


if __name__ == '__main__':
    raise SystemExit(main())
