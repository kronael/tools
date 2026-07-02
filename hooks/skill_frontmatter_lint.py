#!/usr/bin/env python3
"""Check SKILL.md frontmatter with PyYAML; fix common loose scalars."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import yaml

BOUNDARY = re.compile(r'^---\s*$', re.MULTILINE)
FIX_FIELDS = {'description', 'when_to_use'}


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


def process(path: Path, write: bool) -> int:
    split = frontmatter(path.read_text())
    if split is None:
        print(f'{path}: missing frontmatter', file=sys.stderr)
        return 2

    meta, body = split
    error = yaml_error(meta)
    if error is None:
        return 0
    if not write:
        print(f'needs fix: {path} ({error})')
        return 1

    fixed = fix_frontmatter(meta)
    error = yaml_error(fixed)
    if error is not None:
        print(f'{path}: still invalid after fix: {error}', file=sys.stderr)
        return 2

    path.write_text(f'---\n{fixed}---\n\n{body}')
    print(f'fixed: {path}')
    return 1


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
