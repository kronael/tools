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


def sibling(path: Path, rel: str, text: str = 'data\n') -> Path:
    doc = path.parent / rel
    doc.parent.mkdir(parents=True, exist_ok=True)
    doc.write_text(text)
    return doc


def test_unnamed_sibling_is_an_orphan(tmp_path: Path) -> None:
    path = make(tmp_path, VALID)
    sibling(path, 'lonely.md')
    assert 'skill-orphan' in rules(findings(path), Severity.ERROR)
    assert process(path, write=False) == 2


def test_named_sibling_is_reachable(tmp_path: Path) -> None:
    path = make(tmp_path, VALID + '\n- Read `lonely.md` for the rest.\n')
    sibling(path, 'lonely.md')
    assert findings(path) == []


def test_reachability_chains_through_a_named_sibling(tmp_path: Path) -> None:
    path = make(tmp_path, VALID + '\n- Read `index.md`.\n')
    sibling(path, 'index.md', 'See `deep/leaf.md`.\n')
    sibling(path, 'deep/leaf.md')
    assert findings(path) == []


def test_path_style_reference_names_the_basename(tmp_path: Path) -> None:
    path = make(tmp_path, VALID + '\n- Read `flavors/remotion.md`.\n')
    sibling(path, 'flavors/remotion.md')
    assert findings(path) == []


def test_longer_name_does_not_satisfy_its_suffix(tmp_path: Path) -> None:
    """`contexts.md` must not count as a reference to `ts.md`."""
    path = make(tmp_path, VALID + '\n- Read `contexts.md`.\n')
    sibling(path, 'contexts.md')
    sibling(path, 'ts.md')
    messages = [f.message for f in findings(path) if f.rule == 'skill-orphan']
    assert len(messages) == 1
    assert 'ts.md' in messages[0]


def test_claude_md_needs_no_reference(tmp_path: Path) -> None:
    path = make(tmp_path, VALID)
    sibling(path, 'CLAUDE.md')
    assert findings(path) == []


def test_absolute_home_path_fails(tmp_path: Path) -> None:
    path = make(tmp_path, VALID + '\n- Run it in /home/devuser/src/tools.\n')
    assert 'skill-local-path' in rules(findings(path), Severity.ERROR)


def test_hooks_tree_ships_no_home_path() -> None:
    """hooks/ runs on other machines, so a literal home path here is the leak."""
    home = str(Path.home())
    tree = Path(__file__).parent
    leaking = [
        p.relative_to(tree).as_posix()
        for pattern in ('**/*.py', '**/*.md', '**/*.sh')
        for p in sorted(tree.glob(pattern))
        if home in p.read_text()
    ]
    assert leaking == []


def test_placeholder_home_path_passes(tmp_path: Path) -> None:
    path = make(tmp_path, VALID + '\n- The slug of /home/u/app/x is -home-u-app-x.\n')
    assert findings(path) == []


def test_secret_in_a_sibling_fails(tmp_path: Path) -> None:
    path = make(tmp_path, VALID + '\n- Read `creds.md`.\n')
    sibling(path, 'creds.md', 'export TOKEN=sk-ant-oat01-abcdefgh\n')
    assert 'skill-secret' in rules(findings(path), Severity.ERROR)
