#!/usr/bin/env python3
"""Prove every ast-grep lint rule against its fixtures.

Convention: every file under `skills/<lang>/lints/fixtures/` is a fixture. Its
first path component below `fixtures/` names the rule and the expectation:
`<rule-id>.bad.<ext>` or `<rule-id>.bad.d/...` MUST trip `<rule-id>` in every
blank-line-separated block; `<rule-id>.good.<ext>` or `<rule-id>.good.d/...`
MUST stay clean. A `.d/` directory holds fixtures whose path is the point, such
as files a rule's `ignores` skip. Rules live co-located with the language skill
that owns them; `sgconfig.yml` lists the dirs. Run from the repo root (ast-grep
finds `sgconfig.yml` there). Scans run with `--warning`, so a rule promoted to
error still exits 0; any non-zero exit or stderr output is ast-grep failing and
aborts the run. Exit 0 = all rules proven.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml


def case_name(path: Path) -> str:
    parts = path.parts
    return parts[parts.index('fixtures') + 1]


def rule_id(path: Path) -> str:
    return case_name(path).split('.bad.')[0].split('.good.')[0]


def is_bad(path: Path) -> bool:
    return '.bad.' in case_name(path)


def declared_rules() -> dict[str, Path]:
    rules: dict[str, Path] = {}
    for rule_file in sorted(Path('skills').glob('*/lints/rules.yml')):
        for doc in yaml.safe_load_all(rule_file.read_text()):
            if isinstance(doc, dict) and 'id' in doc:
                rules[doc['id']] = rule_file
    return rules


def missing_fixtures(fixtures: list[Path]) -> list[str]:
    have_bad = {rule_id(p) for p in fixtures if is_bad(p)}
    have_good = {rule_id(p) for p in fixtures if not is_bad(p)}
    failures = []
    for rule, source in declared_rules().items():
        for kind, have in (('bad', have_bad), ('good', have_good)):
            if rule not in have:
                failures.append(f'{source}: rule {rule} has no .{kind}. fixture')
    return failures


def matches(path: Path) -> list[dict]:
    result = subprocess.run(
        ['ast-grep', 'scan', '--warning', '--json=compact', str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or result.stderr.strip():
        err = result.stderr.strip()
        msg = f'ast-grep scan {path} exited {result.returncode}: {err}'
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
    found = matches(path)
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
    probe = subprocess.run(['ast-grep', '--version'], capture_output=True, check=False)
    if probe.returncode != 0:
        print('ast-grep not found on PATH', file=sys.stderr)
        return 2

    fixtures = sorted(p for p in Path('skills').glob('*/lints/fixtures/**/*') if p.is_file())
    if not fixtures:
        print('no lint fixtures found')
        return 0

    binding = missing_fixtures(fixtures)
    behavior = [msg for path in fixtures if (msg := check(path))]
    for msg in binding + behavior:
        print(msg, file=sys.stderr)
    print(
        f'{len(fixtures) - len(behavior)}/{len(fixtures)} fixtures behave; {len(binding)} binding gaps'
    )
    return 1 if binding or behavior else 0


if __name__ == '__main__':
    raise SystemExit(main())
