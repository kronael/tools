from pathlib import Path

from skill_frontmatter_lint import Severity
from skill_frontmatter_lint import check_body
from skill_frontmatter_lint import frontmatter
from skill_frontmatter_lint import parse_meta
from skill_frontmatter_lint import process

VALID = """---
name: demo
description: Do the demo thing. NOT for real work (use other).
when_to_use: demo, example, trigger words
---

# Demo

- ALWAYS do X.
- NEVER do Y.
"""


def make(tmp_path: Path, text: str, name: str = 'demo') -> Path:
    directory = tmp_path / name
    directory.mkdir(exist_ok=True)
    path = directory / 'SKILL.md'
    path.write_text(text)
    return path


def findings(path: Path) -> list:
    text = path.read_text()
    split = frontmatter(text)
    assert split is not None
    meta, body = split
    return check_body(path, text, parse_meta(meta), body)


def rules(items: list, severity: Severity) -> set[str]:
    return {item.rule for item in items if item.severity is severity}


def test_valid_skill_passes(tmp_path: Path) -> None:
    assert findings(make(tmp_path, VALID)) == []
    assert process(make(tmp_path, VALID), write=False) == 0


def test_missing_key_fails(tmp_path: Path) -> None:
    text = VALID.replace('when_to_use: demo, example, trigger words\n', '')
    assert 'skill-keys' in rules(findings(make(tmp_path, text)), Severity.ERROR)


def test_unknown_key_fails(tmp_path: Path) -> None:
    text = VALID.replace('when_to_use:', 'arg: <x>\nwhen_to_use:')
    assert 'skill-keys' in rules(findings(make(tmp_path, text)), Severity.ERROR)


def test_name_must_match_directory(tmp_path: Path) -> None:
    path = make(tmp_path, VALID, name='other')
    assert 'skill-name' in rules(findings(path), Severity.ERROR)
    assert process(path, write=False) == 2


def test_should_in_body_fails(tmp_path: Path) -> None:
    path = make(tmp_path, VALID + '\n- You SHOULD do X.\n')
    assert 'skill-should' in rules(findings(path), Severity.ERROR)
    assert process(path, write=False) == 2


def test_over_cap_warns_never_errors(tmp_path: Path) -> None:
    long_body = '\n'.join(f'- line {i}' for i in range(250))
    path = make(tmp_path, VALID + long_body)
    found = findings(path)
    assert 'skill-length' in rules(found, Severity.WARN)
    assert 'skill-length' not in rules(found, Severity.ERROR)


def test_over_listing_cap_warns(tmp_path: Path) -> None:
    text = VALID.replace(
        'when_to_use: demo, example, trigger words\n',
        'when_to_use: ' + ', '.join(f'phrase {i}' for i in range(200)) + '\n',
    )
    found = findings(make(tmp_path, text))
    assert 'skill-budget' in rules(found, Severity.WARN)
    assert 'skill-budget' not in rules(found, Severity.ERROR)


def test_allowlisted_skill_gets_higher_cap(tmp_path: Path) -> None:
    long_body = '\n'.join(f'- line {i}' for i in range(250))
    path = make(tmp_path, VALID + long_body, name='ship')
    assert 'skill-length' not in rules(findings(path), Severity.WARN)


def test_nested_skill_md_warns(tmp_path: Path) -> None:
    top = tmp_path / 'router'
    top.mkdir()
    (top / 'SKILL.md').write_text(VALID)
    nested_dir = top / 'mode'
    nested_dir.mkdir()
    nested = nested_dir / 'SKILL.md'
    nested.write_text(VALID)
    assert 'skill-router' in rules(findings(nested), Severity.WARN)


def test_missing_notfor_warns(tmp_path: Path) -> None:
    text = VALID.replace(' NOT for real work (use other).', '')
    assert 'skill-notfor' in rules(findings(make(tmp_path, text)), Severity.WARN)
