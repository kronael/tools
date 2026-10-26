#!/usr/bin/env python3
"""Scan explicit project paths with --scan; otherwise verify the bundled fixtures.

Exit 0: clean; 1: findings or failed fixtures/bindings; 2: failed check.
Fixture naming and adoption: lints.md beside this script.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[1]


def case_name(path: Path) -> str:
    parts = path.parts
    return parts[parts.index('fixtures') + 1]


def rule_id(path: Path) -> str:
    return case_name(path).split('.bad.')[0].split('.good.')[0]


def is_bad(path: Path) -> bool:
    return '.bad.' in case_name(path)


def declared_rules() -> dict[str, Path]:
    import yaml  # noqa: PLC0415 - fixture-only dependency; scans use the standard library

    rules: dict[str, Path] = {}
    for rule_file in sorted(SKILLS.glob('*/lints/rules.yml')):
        for doc in yaml.safe_load_all(rule_file.read_text()):
            if isinstance(doc, dict) and 'id' in doc:
                if doc['id'] in rules:
                    raise ValueError(f'duplicate rule id: {doc["id"]}')
                rules[doc['id']] = rule_file
    return rules


def missing_fixtures(fixtures: list[Path]) -> list[str]:
    import yaml  # noqa: PLC0415 - fixture-only dependency; scans use the standard library

    have_bad = {rule_id(p) for p in fixtures if is_bad(p)}
    have_good = {rule_id(p) for p in fixtures if not is_bad(p)}
    failures = []
    rules = declared_rules()
    for rule, source in rules.items():
        for kind, have in (('bad', have_bad), ('good', have_good)):
            if rule not in have:
                failures.append(f'{source}: rule {rule} has no .{kind}. fixture')
    failures.extend(
        f'{path}: fixture names an undeclared rule'
        for path in fixtures
        if rule_id(path) not in rules
    )
    config = SKILLS.parent / 'sgconfig.yml'
    configured = {
        (config.parent / path).resolve() for path in yaml.safe_load(config.read_text())['ruleDirs']
    }
    expected = {path.parent for path in rules.values()}
    if configured != expected:
        failures.append(f'{config}: ruleDirs differ from the bundled rule directories')
    return failures


def matches(paths: list[Path]) -> list[dict]:
    rule_files = sorted(SKILLS.glob('*/lints/rules.yml'))
    if not rule_files:
        raise ValueError(f'no lint rules found under {SKILLS}')
    for path in paths:
        if not path.exists():
            raise FileNotFoundError(path)
    result = subprocess.run(
        [
            'ast-grep',
            'scan',
            '--warning',
            '--json=compact',
            '--inline-rules=' + '\n'.join(path.read_text() for path in rule_files),
            '--',
            *(str(path) for path in paths),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or result.stderr.strip():
        err = result.stderr.strip()
        msg = f'ast-grep scan exited {result.returncode}: {err}'
        raise RuntimeError(msg)
    return json.loads(result.stdout)


def blocks(path: Path) -> list[tuple[int, int]]:
    spans = []
    start = None
    lines = path.read_text().splitlines()
    for n, line in enumerate(lines):
        if line.strip() and start is None:
            start = n
        elif not line.strip() and start is not None:
            spans.append((start, n - 1))
            start = None
    if start is not None:
        spans.append((start, len(lines) - 1))
    return spans


def check(path: Path) -> str | None:
    found = matches([path])
    rule = rule_id(path)
    if not is_bad(path):
        if found:
            return f'{path}: expected no matches, got {sorted({m["ruleId"] for m in found})}'
        return None
    hits = [
        (m['range']['start']['line'], m['range']['end']['line'])
        for m in found
        if m['ruleId'] == rule
    ]
    missed = [
        first + 1
        for first, last in blocks(path)
        if not any(start <= last and end >= first for start, end in hits)
    ]
    if missed:
        return f'{path}: expected rule {rule} to fire in the block at line(s) {missed}'
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        '--scan',
        nargs='+',
        type=Path,
        metavar='PATH',
        help='scan these files/directories; exit 1 on findings, 2 on failure',
    )
    args = parser.parse_args()
    if args.scan is not None:
        found = matches(args.scan)
        for match in found:
            start = match['range']['start']
            print(
                f'{match["file"]}:{start["line"] + 1}:{start["column"] + 1}: '
                f'{match["ruleId"]}: {match["message"]}'
            )
        print(f'{len(found)} lint findings')
        return int(bool(found))

    fixtures = sorted(p for p in SKILLS.glob('*/lints/fixtures/**/*') if p.is_file())
    if not fixtures:
        raise ValueError('no lint fixtures found')

    binding = missing_fixtures(fixtures)
    behavior = [msg for path in fixtures if (msg := check(path))]
    for msg in binding + behavior:
        print(msg, file=sys.stderr)
    print(
        f'{len(fixtures) - len(behavior)}/{len(fixtures)} fixtures behave; {len(binding)} binding gaps'
    )
    return 1 if binding or behavior else 0


if __name__ == '__main__':
    try:
        status = main()
    except (OSError, RuntimeError, ValueError) as exc:
        print(f'lint check failed: {exc}', file=sys.stderr)
        status = 2
    raise SystemExit(status)
