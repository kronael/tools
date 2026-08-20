#!/usr/bin/env python3
"""Prove every ast-grep lint rule against its fixtures.

Convention: `skills/<lang>/lints/fixtures/<rule-id>.bad.<ext>` MUST trip
`<rule-id>`; `<rule-id>.good.<ext>` MUST stay clean. Rules live co-located with
the language skill that owns them; `sgconfig.yml` lists the dirs. Run from the
repo root (ast-grep finds `sgconfig.yml` there). Exit 0 = all rules proven.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml


def rule_id(path: Path) -> str:
    """`ts-no-push-spread.bad.ts` -> `ts-no-push-spread`."""
    return path.name.split('.bad.')[0].split('.good.')[0]


def declared_rules() -> dict[str, Path]:
    """Every rule id across the co-located `skills/<lang>/lints/rules.yml`."""
    rules: dict[str, Path] = {}
    for rule_file in sorted(Path('skills').glob('*/lints/rules.yml')):
        for doc in yaml.safe_load_all(rule_file.read_text()):
            if isinstance(doc, dict) and 'id' in doc:
                rules[doc['id']] = rule_file
    return rules


def missing_fixtures(fixtures: list[Path]) -> list[str]:
    """Every declared rule needs a paired .bad. and .good. fixture."""
    have_bad = {rule_id(p) for p in fixtures if '.bad.' in p.name}
    have_good = {rule_id(p) for p in fixtures if '.good.' in p.name}
    failures = []
    for rule, source in declared_rules().items():
        for kind, have in (('bad', have_bad), ('good', have_good)):
            if rule not in have:
                failures.append(f'{source}: rule {rule} has no .{kind}. fixture')
    return failures


def matched_rules(path: Path) -> set[str]:
    """Rule ids ast-grep fires on one file, using the repo sgconfig."""
    result = subprocess.run(
        ['ast-grep', 'scan', '--json=compact', str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    return {match['ruleId'] for match in json.loads(result.stdout or '[]')}


def check(path: Path) -> str | None:
    """Return a failure message, or None if the fixture behaves."""
    fired = matched_rules(path)
    rule = rule_id(path)
    if '.bad.' in path.name and rule not in fired:
        return f'{path}: expected rule {rule} to fire, got {sorted(fired) or "none"}'
    if '.good.' in path.name and fired:
        return f'{path}: expected no matches, got {sorted(fired)}'
    return None


def main() -> int:
    probe = subprocess.run(['ast-grep', '--version'], capture_output=True, check=False)
    if probe.returncode != 0:
        print('ast-grep not found on PATH', file=sys.stderr)
        return 2

    fixtures = sorted(Path('skills').glob('*/lints/fixtures/*.*'))
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
