from pathlib import Path

from skill_frontmatter_lint import Severity
from spec_lint import check_corpus
from spec_lint import report
from spec_lint import spec_roots

INDEX = """| Spec | Status | Summary |
|------|--------|---------|
| [01-auth.md](01-auth.md) | shipped | JWT auth flow |
"""

SPEC = """---
status: shipped
---

# Auth

Tokens are verified once, at the edge — `src/config.py:3` holds the key.
"""


def corpus(tmp_path: Path, index: str = INDEX, spec: str = SPEC, name: str = '01-auth.md') -> Path:
    root = tmp_path / 'specs'
    root.mkdir(exist_ok=True)
    (tmp_path / 'src').mkdir(exist_ok=True)
    (tmp_path / 'src' / 'config.py').write_text('KEY = 1\n')
    if index:
        (root / 'index.md').write_text(index)
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(spec)
    return root


def rules(root: Path, severity: Severity) -> set[str]:
    return {item.rule for item in check_corpus(root) if item.severity is severity}


def test_clean_corpus_passes(tmp_path: Path) -> None:
    root = corpus(tmp_path)
    assert check_corpus(root) == []
    assert report(root) == 0


def test_unknown_status_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC.replace('shipped', 'proposed'))
    assert 'spec-status' in rules(root, Severity.ERROR)
    assert report(root) == 2


def test_missing_frontmatter_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec='# Auth\n')
    assert 'spec-status' in rules(root, Severity.ERROR)


def test_index_status_prose_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, index=INDEX.replace('| shipped |', '| active — superseded by 02 |'))
    assert 'spec-status' in rules(root, Severity.ERROR)


def test_missing_index_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, index='')
    assert 'spec-index-row' in rules(root, Severity.ERROR)


def test_unlisted_spec_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path)
    (root / '02-webhooks.md').write_text(SPEC)
    assert 'spec-index-row' in rules(root, Severity.ERROR)


def test_dangling_index_link_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, index=INDEX.replace('(01-auth.md)', '(01-athu.md)'))
    found = rules(root, Severity.ERROR)
    assert 'spec-index-dangling' in found
    assert 'spec-index-row' in found


def test_unnumbered_name_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, index=INDEX.replace('01-auth.md', 'auth.md'), name='auth.md')
    assert 'spec-naming' in rules(root, Severity.ERROR)


def test_too_deep_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path)
    deep = root / '1' / 'sub'
    deep.mkdir(parents=True)
    (deep / '2-webhooks.md').write_text(SPEC)
    assert 'spec-naming' in rules(root, Severity.ERROR)


def test_phase_name_passes(tmp_path: Path) -> None:
    index = INDEX.replace('01-auth.md', '1/2-webhooks.md')
    assert check_corpus(corpus(tmp_path, index=index, name='1/2-webhooks.md')) == []


def test_unpadded_flat_number_warns(tmp_path: Path) -> None:
    root = corpus(tmp_path, index=INDEX.replace('01-auth.md', '1-auth.md'), name='1-auth.md')
    assert 'spec-naming' in rules(root, Severity.WARN)
    assert 'spec-naming' not in rules(root, Severity.ERROR)
    assert report(root) == 0


def test_tbd_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + '\nRotation interval: TBD.\n')
    assert 'spec-tbd' in rules(root, Severity.ERROR)


def test_tbd_inside_fence_is_ignored(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + '\n```python\n# TODO: upstream bug\n```\n')
    assert check_corpus(root) == []


def test_future_tense_warns(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + '\nWe will move the check into the router.\n')
    assert 'spec-future-tense' in rules(root, Severity.WARN)
    assert 'spec-future-tense' not in rules(root, Severity.ERROR)
    assert report(root) == 0


def test_unresolved_pointer_warns(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', 'src/gone.py:3'))
    assert 'spec-pointer' in rules(root, Severity.WARN)
    assert report(root) == 0


def test_prose_backtick_is_not_a_pointer(tmp_path: Path) -> None:
    root = corpus(
        tmp_path, spec=SPEC + '\nThe key lives in `config.yaml`, never in `$HOME/.env`.\n'
    )
    assert check_corpus(root) == []


def test_test_suite_named_specs_is_not_discovered(tmp_path: Path) -> None:
    suite = tmp_path / 'e2e' / 'specs' / 'server'
    suite.mkdir(parents=True)
    (suite / 'auth.md').write_text('# auth case\n')
    assert spec_roots([tmp_path]) == []


def test_skill_dir_named_specs_has_no_root(tmp_path: Path) -> None:
    skill = tmp_path / 'skills' / 'specs'
    skill.mkdir(parents=True)
    skill_file = skill / 'SKILL.md'
    skill_file.write_text('# Specs skill\n')
    (skill / 'format.md').write_text('# Format\n')
    assert spec_roots([skill_file]) == []
