# pyright: basic
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

from speclint import Severity
from speclint import check_corpus
from speclint import check_pointers
from speclint import indexed_files
from speclint import run
from speclint import spec_roots

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


@pytest.fixture(autouse=True)
def fresh_index(tmp_path: Path):
    indexed_files.cache_clear()
    (tmp_path / '.git').write_text('gitdir: elsewhere\n')


@pytest.fixture
def locked(tmp_path: Path):
    if os.geteuid() == 0:
        pytest.skip('root reads a mode-000 directory')
    path = tmp_path / 'secrets'
    (path / '.git').mkdir(parents=True)
    path.chmod(0)
    yield path
    path.chmod(0o755)


def corpus(tmp_path: Path, index: str = INDEX, spec: str = SPEC, name: str = '01-auth.md') -> Path:
    root = tmp_path / 'specs'
    root.mkdir(parents=True, exist_ok=True)
    (tmp_path / 'src').mkdir(exist_ok=True)
    (tmp_path / 'src' / 'config.py').write_text('KEY = 1\nSALT = 2\nTTL = 3\n')
    if index:
        (root / 'index.md').write_text(index)
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(spec)
    return root


def component_corpus(tmp_path: Path, spec: str) -> Path:
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / '.git').write_text('gitdir: elsewhere\n')
    root = corpus(tmp_path / 'app', spec=spec)
    (tmp_path / 'lib').mkdir()
    (tmp_path / 'lib' / 'shared.py').write_text('X = 1\n')
    return root


def rules(root: Path, severity: Severity) -> set[str]:
    return {item.rule for item in check_corpus(root) if item.severity is severity}


def touch(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('x\n' * 2000)


def test_clean_corpus_passes(tmp_path: Path) -> None:
    root = corpus(tmp_path)
    assert check_corpus(root) == []
    assert run([root], verbose=False) == 0


def test_unknown_status_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC.replace('shipped', 'proposed'))
    assert 'spec-status' in rules(root, Severity.ERROR)
    assert run([root], verbose=False) == 1


def test_missing_frontmatter_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec='# Auth\n')
    assert 'spec-status' in rules(root, Severity.ERROR)


def test_quoted_status_passes(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC.replace('status: shipped', 'status: "shipped"'))
    assert check_corpus(root) == []


def test_index_status_prose_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, index=INDEX.replace('| shipped |', '| active — superseded by 02 |'))
    assert 'spec-status' in rules(root, Severity.ERROR)


def test_index_status_mismatch_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, index=INDEX.replace('| shipped |', '| draft |'))
    assert 'spec-status' in rules(root, Severity.ERROR)
    assert run([root], verbose=False) == 1


def test_prose_link_does_not_count_as_index_row(tmp_path: Path) -> None:
    root = corpus(tmp_path, index='See [auth](01-auth.md).\n')
    assert 'spec-index-row' in rules(root, Severity.ERROR)


def test_summary_link_does_not_count_as_spec_row(tmp_path: Path) -> None:
    root = corpus(tmp_path, index=INDEX.replace('JWT auth flow', '[webhooks](02-webhooks.md)'))
    (root / '02-webhooks.md').write_text(SPEC)
    assert 'spec-index-row' in rules(root, Severity.ERROR)


def test_index_anchor_links_match_spec_status(tmp_path: Path) -> None:
    root = corpus(tmp_path, index=INDEX.replace('(01-auth.md)', '(01-auth.md#auth)'))
    assert check_corpus(root) == []


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
    assert run([root], verbose=False) == 0


def test_corpus_under_a_generated_dir_name_is_checked(tmp_path: Path) -> None:
    root = corpus(tmp_path / 'build' / 'app', spec=SPEC.replace('shipped', 'invalid'))
    assert 'spec-status' in rules(root, Severity.ERROR)


def test_status_with_a_yaml_comment_passes(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC.replace('status: shipped', 'status: shipped  # landed'))
    assert check_corpus(root) == []


def test_unresolved_pointer_warns(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', 'src/gone.py:3'))
    found = check_corpus(root)
    assert [item.rule for item in found] == ['spec-pointer']
    assert 'does not resolve under' in found[0].message
    assert run([root], verbose=False) == 0


@pytest.mark.parametrize(
    'example',
    [
        '```\n`src/example.py`\n```',
        '> ```\n> `src/example.py`\n> ```',
        '- ```\n  `src/example.py`\n  ```',
        '> - ```\n>   `src/example.py`\n>   ```',
        '<!-- `src/example.py` -->',
        r'\`src/example.py\`',
    ],
)
def test_pointer_only_in_markdown_prose(tmp_path, example):
    root = corpus(tmp_path)
    text = example + '\n\n`src/real.py`\n'
    found = check_pointers(root, root / '01-auth.md', text)
    assert len(found) == 1
    assert f':{len(example.splitlines()) + 2}: [spec-pointer]' in found[0].message
    assert '`src/real.py`' in found[0].message


def test_pointer_line_in_multiline_prose_and_table(tmp_path):
    root = corpus(tmp_path)
    text = (
        'First line `src/one.py`\n`src/two.py` and `src/three.py`\n\n'
        '| Example |\n|---|\n| `src/four.py` |\n'
    )
    found = check_pointers(root, root / '01-auth.md', text)
    assert [item.message.split(': [spec-pointer]')[0].rsplit(':', 1)[1] for item in found] == [
        '1',
        '2',
        '2',
        '6',
    ]


def test_prose_backtick_is_not_a_pointer(tmp_path: Path) -> None:
    root = corpus(
        tmp_path, spec=SPEC + '\nThe key lives in `config.yaml`, never in `$HOME/.env`.\n'
    )
    assert check_corpus(root) == []


def test_bare_basename_with_line_resolves_when_unique(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', 'planning.py:1599-1645'))
    touch(tmp_path / 'tools' / 'graph' / 'planning.py')
    assert check_corpus(root) == []


def test_bare_basename_shared_by_two_files_warns(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', 'page.tsx:21'))
    touch(tmp_path / 'app' / 'page.tsx')
    touch(tmp_path / 'app' / 'login' / 'page.tsx')
    found = check_corpus(root)
    assert [item.rule for item in found] == ['spec-pointer']
    assert 'matches 2 files' in found[0].message


def test_subpackage_relative_path_resolves_by_tail(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', 'api/start.sh'))
    touch(tmp_path / 'src' / 'api' / 'start.sh')
    assert check_corpus(root) == []


def test_repo_root_path_resolves_from_component_specs(tmp_path: Path) -> None:
    root = component_corpus(tmp_path, SPEC.replace('src/config.py:3', 'app/src/config.py:3'))
    assert check_corpus(root) == []


def test_sibling_component_path_resolves(tmp_path: Path) -> None:
    root = component_corpus(tmp_path, SPEC.replace('src/config.py:3', 'lib/shared.py'))
    assert check_corpus(root) == []


def test_component_copy_wins_over_sibling_copy(tmp_path: Path) -> None:
    root = component_corpus(tmp_path, SPEC.replace('src/config.py:3', 'providers.tsx:8'))
    touch(tmp_path / 'app' / 'ui' / 'providers.tsx')
    touch(tmp_path / 'lib' / 'ui' / 'providers.tsx')
    assert check_corpus(root) == []


def test_nested_repo_is_not_searched(tmp_path: Path) -> None:
    root = component_corpus(tmp_path, SPEC.replace('src/config.py:3', 'planning.py:1'))
    touch(tmp_path / '.other-checkout' / 'planning.py')
    (tmp_path / '.other-checkout' / '.git').write_text('gitdir: elsewhere\n')
    assert 'spec-pointer' in rules(root, Severity.WARN)


def test_file_above_repo_root_is_not_found(tmp_path: Path) -> None:
    root = component_corpus(tmp_path / 'repo', SPEC.replace('src/config.py:3', 'outside.py:1'))
    touch(tmp_path / 'outside.py')
    assert 'spec-pointer' in rules(root, Severity.WARN)


def test_test_suite_named_specs_is_not_discovered(tmp_path: Path) -> None:
    suite = tmp_path / 'e2e' / 'specs' / 'server'
    suite.mkdir(parents=True)
    (suite / 'auth.md').write_text('# auth case\n')
    assert spec_roots([tmp_path]) == []
    assert spec_roots([suite.parent.parent]) == []
    assert spec_roots([suite / 'auth.md']) == []


def test_explicit_unnumbered_corpus_is_checked(tmp_path: Path) -> None:
    root = corpus(tmp_path, index='', name='auth.md')
    assert spec_roots([root]) == [root]
    found = rules(root, Severity.ERROR)
    assert 'spec-naming' in found
    assert 'spec-index-row' in found


def test_file_trigger_discovers_valid_corpus(tmp_path: Path) -> None:
    root = corpus(tmp_path)
    assert spec_roots([root / '01-auth.md']) == [root]
    assert spec_roots([tmp_path]) == [root]


def test_discovery_stops_at_nested_repos(tmp_path: Path) -> None:
    root = corpus(tmp_path)
    corpus(tmp_path / '.worktree')
    (tmp_path / '.worktree' / '.git').write_text('gitdir: elsewhere\n')
    assert spec_roots([tmp_path]) == [root]


def test_skill_dir_named_specs_has_no_root(tmp_path: Path) -> None:
    skill = tmp_path / 'skills' / 'specs'
    skill.mkdir(parents=True)
    skill_file = skill / 'SKILL.md'
    skill_file.write_text('# Specs skill\n')
    (skill / 'format.md').write_text('# Format\n')
    assert spec_roots([skill_file]) == []


def test_diary_date_placeholder_is_not_a_pointer(tmp_path: Path) -> None:
    root = corpus(
        tmp_path, spec=SPEC + '\nLogged to `.diary/YYYYMMDD.md` after significant work.\n'
    )
    assert check_corpus(root) == []


def test_claude_md_in_specs_is_not_a_spec(tmp_path: Path) -> None:
    root = corpus(tmp_path)
    (root / 'CLAUDE.md').write_text('# Instructions\n')
    assert check_corpus(root) == []


def test_phase_index_row_counts_when_root_links_it(tmp_path: Path) -> None:
    index = '| Phase | Index |\n|---|---|\n| 1 | [specs](1/index.md) |\n'
    root = corpus(tmp_path, index=index, name='1/2-webhooks.md')
    (root / '1' / 'index.md').write_text(INDEX.replace('01-auth.md', '2-webhooks.md'))
    assert check_corpus(root) == []


def test_phase_index_status_mismatch_fails(tmp_path: Path) -> None:
    index = '| Phase | Index |\n|---|---|\n| 1 | [specs](1/index.md) |\n'
    root = corpus(tmp_path, index=index, name='1/2-webhooks.md')
    phase = INDEX.replace('01-auth.md', '2-webhooks.md').replace('| shipped |', '| draft |')
    (root / '1' / 'index.md').write_text(phase)
    assert 'spec-status' in rules(root, Severity.ERROR)


def test_phase_row_in_a_three_column_root_index_passes(tmp_path: Path) -> None:
    index = '| Phase | Specs | Note |\n|---|---|---|\n| [Phase 1](1/index.md) | 1 spec | x |\n'
    root = corpus(tmp_path, index=index, name='1/2-webhooks.md')
    (root / '1' / 'index.md').write_text(INDEX.replace('01-auth.md', '2-webhooks.md'))
    assert check_corpus(root) == []


def test_root_relative_and_encoded_links_resolve(tmp_path: Path) -> None:
    root = component_corpus(
        tmp_path, SPEC + '\nSee [shared](/lib/shared.py) and [notes](notes%20v2.md "Notes").\n'
    )
    (root / 'notes v2.md').write_text(SPEC.replace('shipped', 'reference'))
    index = INDEX + '| [notes v2.md](notes%20v2.md) | reference | Notes |\n'
    (root / 'index.md').write_text(index)
    found = check_corpus(root)
    assert [item.rule for item in found] == ['spec-naming']


def test_unlinked_phase_index_does_not_count(tmp_path: Path) -> None:
    root = corpus(tmp_path, index='# Specs\n', name='1/2-webhooks.md')
    (root / '1' / 'index.md').write_text(INDEX.replace('01-auth.md', '2-webhooks.md'))
    assert 'spec-index-row' in rules(root, Severity.ERROR)


def test_shared_number_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, index=INDEX + '| [01-sync.md](01-sync.md) | shipped | Sync |\n')
    (root / '01-sync.md').write_text(SPEC)
    found = [item for item in check_corpus(root) if item.rule == 'spec-naming']
    assert len(found) == 1
    assert found[0].severity is Severity.ERROR
    assert 'number shared with 01-sync.md' in found[0].message


def test_resolving_scheme_anchor_and_quoted_links_pass(tmp_path: Path) -> None:
    root = corpus(
        tmp_path,
        spec=SPEC + '\nSee [key](../src/config.py), [top](#auth), [btc](asset:btc), '
        '[docs](https://example.test/x), [this](<path>) and the shape `[x](gone.md)`.\n',
    )
    assert check_corpus(root) == []


def test_pointer_past_the_end_warns(tmp_path: Path) -> None:
    for anchor in 'src/config.py:40-52', 'src/config.py:2-999', 'src/config.py:0':
        root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', anchor))
        found = [item for item in check_corpus(root) if item.rule == 'spec-pointer']
        assert len(found) == 1, anchor
        assert 'past the end of the file (3 lines)' in found[0].message
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', 'src/config.py:1-3'))
    assert check_corpus(root) == []


def test_missing_path_exits_2(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run([tmp_path / 'nowhere'], verbose=False) == 2
    assert 'no such file or directory' in capsys.readouterr().err


def test_no_corpus_exits_0_with_a_note(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run([tmp_path], verbose=False) == 0
    assert 'no spec corpus under' in capsys.readouterr().err


def test_findings_and_summary_go_to_stdout(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    root = corpus(tmp_path, spec=SPEC.replace('shipped', 'invalid'))
    assert run([root], verbose=True) == 1
    out = capsys.readouterr().out
    assert out.startswith(f'checking {root}\n')
    assert '[spec-status]' in out
    assert out.rstrip().endswith('speclint: 1 errors, 0 warnings')


def test_help_names_rules_and_exit_codes() -> None:
    result = subprocess.run(
        [sys.executable, '-m', 'speclint', '--help'], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert 'spec-pointer' in result.stdout
    assert 'exit codes' in result.stdout


@pytest.mark.usefixtures('locked')
def test_unreadable_dir_fails(tmp_path: Path) -> None:
    root = component_corpus(tmp_path, SPEC.replace('src/config.py:3', 'planning.py:1'))
    touch(tmp_path / 'tools' / 'planning.py')
    assert run([tmp_path], verbose=False) == 2
    assert run([root], verbose=False) == 2


def test_broken_spec_symlink_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path)
    (root / '02-link.md').symlink_to(root / 'gone.md')
    (root / '03-notes.md').mkdir()
    assert run([root], verbose=False) == 2


def test_path_without_an_extension_is_a_pointer(tmp_path: Path) -> None:
    (tmp_path / 'rig').mkdir()
    (tmp_path / 'rig' / 'rig').write_text('#!/bin/sh\n')
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', 'rig/rig:999'))
    found = check_corpus(root)
    assert [item.rule for item in found] == ['spec-pointer']
    assert 'past the end of the file (1 lines)' in found[0].message
    touch(tmp_path / 'server' / 'Makefile')
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', 'server/Makefile'))
    assert check_corpus(root) == []
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', 'server/Gonefile'))
    assert [item.rule for item in check_corpus(root)] == ['spec-pointer']


def test_host_port_and_directory_are_not_pointers(tmp_path: Path) -> None:
    spec = SPEC + '\nThe API listens on `localhost:3004`; the build lands in `frontend/`.\n'
    assert check_corpus(corpus(tmp_path, spec=spec)) == []


def test_dotdot_path_is_not_resolved(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', '../src/config.py:999'))
    assert check_corpus(root) == []


def test_utf8_spec_reads_and_prints_under_the_c_locale(tmp_path: Path) -> None:
    env = {**os.environ, 'LC_ALL': 'C', 'PYTHONUTF8': '0', 'PYTHONCOERCECLOCALE': '0'}
    for spec, code in (SPEC, 0), (SPEC.replace('shipped', 'invalid'), 1):
        root = corpus(tmp_path, spec=spec)
        result = subprocess.run(
            [sys.executable, '-m', 'speclint', str(root)],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        assert result.returncode == code, result.stderr
        assert 'Traceback' not in result.stderr


def test_spec_with_a_byte_order_mark_has_frontmatter(tmp_path: Path) -> None:
    root = corpus(tmp_path)
    (root / '01-auth.md').write_text('\ufeff' + SPEC, encoding='utf-8')
    assert check_corpus(root) == []


def test_fence_with_an_info_string_does_not_close_a_block(tmp_path: Path) -> None:
    quoted = '\n```\n```bash\n`src/ignored.py:1`\n```\n\n`src/missing.py:1`\n'
    found = check_corpus(corpus(tmp_path, spec=SPEC + quoted))
    assert [item.rule for item in found] == ['spec-pointer']
    assert 'src/missing.py' in found[0].message


def test_help_and_readme_name_the_same_rules(pytestconfig: pytest.Config) -> None:
    result = subprocess.run(
        [sys.executable, '-m', 'speclint', '--help'], capture_output=True, text=True, check=False
    )
    readme = (pytestconfig.rootpath / 'README.md').read_text(encoding='utf-8')
    in_help = set(re.findall(r'^  (spec-[a-z-]+) ', result.stdout, re.MULTILINE))
    in_readme = set(re.findall(r'^\| `(spec-[a-z-]+)` \|', readme, re.MULTILINE))
    assert in_help == in_readme
    assert len(in_help) == 5


@pytest.mark.parametrize(
    'status', ['draft', 'experiment', 'planned', 'partial', 'shipped', 'reference']
)
def test_all_statuses_pass(tmp_path, status):
    root = corpus(
        tmp_path, spec=SPEC.replace('shipped', status), index=INDEX.replace('shipped', status)
    )
    assert check_corpus(root) == []


@pytest.mark.parametrize(
    'header',
    [
        '',
        'status: unknown',
        'status: "shipped',
        "status: shipped'",
        'status: shipped\nstatus: draft',
        'status: shipped\nstatus: shipped',
        'status: [shipped]',
        'status:\n  shipped',
        'status: shipped\nextra: [',
        'status: shipped\n  nested: x',
        'status: shipped#text',
    ],
)
def test_malformed_header_fails(tmp_path, header):
    root = corpus(tmp_path, spec=f'---\n{header}\n---\n# Example\n')
    assert 'spec-status' in rules(root, Severity.ERROR)
    assert run([root], verbose=False) == 1


def test_unclosed_header_fails(tmp_path):
    root = corpus(tmp_path, spec='---\nstatus: shipped\n# Example\n')
    assert 'spec-status' in rules(root, Severity.ERROR)


def test_header_comments_and_crlf_pass(tmp_path):
    root = corpus(tmp_path)
    text = SPEC.replace('status: shipped', "# State\n\nstatus: 'shipped' # Ready")
    (root / '01-auth.md').write_bytes(text.replace('\n', '\r\n').encode())
    assert check_corpus(root) == []


def test_invalid_utf8_fails(tmp_path, capsys):
    root = corpus(tmp_path)
    (root / '01-auth.md').write_bytes(b'\xff')
    assert run([root], verbose=False) == 2
    assert 'Cannot read corpus' in capsys.readouterr().err


@pytest.mark.parametrize('target', ['01-auth.md%00', '%00/index.md'])
def test_invalid_index_path_exits_2(tmp_path, target, capsys):
    root = corpus(tmp_path, index=INDEX.replace('(01-auth.md)', f'({target})'))
    assert run([root], verbose=False) == 2
    assert 'embedded null' in capsys.readouterr().err


@pytest.mark.parametrize('lines', ['9' * 4500, '1-' + '9' * 4500], ids=['start', 'end'])
def test_oversized_pointer_line_exits_2(tmp_path, lines, capsys):
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', f'src/config.py:{lines}'))
    assert run([root], verbose=False) == 2
    assert 'integer string conversion' in capsys.readouterr().err


def test_unreadable_explicit_path_exits_2(locked):
    result = subprocess.run(
        [sys.executable, '-m', 'speclint', str(locked / 'specs')],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 2
    assert result.stderr.startswith('speclint:')
    assert 'Traceback' not in result.stderr


def test_empty_corpus_passes(tmp_path):
    root = tmp_path / 'specs'
    root.mkdir()
    assert run([root], verbose=False) == 0
    (root / 'index.md').write_text('| Spec | Status | Summary |\n|---|---|---|\n')
    assert run([root], verbose=False) == 0


def test_retirement_requires_index_removal(tmp_path):
    root = corpus(tmp_path)
    (root / '01-auth.md').unlink()
    assert rules(root, Severity.ERROR) == {'spec-index-dangling'}
    (root / 'index.md').write_text('# Specs\n')
    assert check_corpus(root) == []
    (root / 'index.md').unlink()
    assert run([tmp_path], verbose=False) == 0


def test_duplicate_index_row_fails(tmp_path):
    root = corpus(tmp_path, index=INDEX + INDEX.splitlines()[-1] + '\n')
    assert 'spec-index-row' in rules(root, Severity.ERROR)


def test_phased_corpus_without_root_index_is_discovered(tmp_path):
    root = corpus(tmp_path, name='1/2-api.md', index='')
    assert spec_roots([tmp_path]) == [root]
    assert spec_roots([root / '1' / '2-api.md']) == [root]
    assert run([tmp_path], verbose=False) == 1


def test_stale_phase_index_fails(tmp_path):
    root = tmp_path / 'specs'
    root.mkdir()
    (root / 'index.md').write_text('[Phase](1/index.md)\n')
    assert rules(root, Severity.ERROR) == {'spec-index-dangling'}


def test_markdown_and_prose_belong_to_other_checks(tmp_path):
    text = """
TODO TBD implement later
We will make a robust harness.
## Alternatives
- [ ] Work
[missing](../gone.md#absent)
```sql
CREATE TABLE sample (id int);
```
"""
    root = corpus(
        tmp_path,
        spec=SPEC + text * 1100,
        index=INDEX
        + '| [02-store.md](02-store.md) | shipped | Store |\n'
        + '\n[Guide](../absent.md)\n',
    )
    (root / '02-store.md').write_text(SPEC + text)
    assert check_corpus(root) == []


def test_status_does_not_require_code_pointers(tmp_path):
    assert check_corpus(corpus(tmp_path, spec='---\nstatus: shipped\n---\n# Example\n')) == []


@pytest.mark.parametrize('pointer', ['src/config.py:0', 'src/config.py:3-2', 'src/config.py:1-4'])
def test_invalid_line_ranges_warn(tmp_path, pointer):
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', pointer))
    assert rules(root, Severity.WARN) == {'spec-pointer'}


def test_pointer_to_directory_warns(tmp_path):
    (tmp_path / 'src' / 'directory').mkdir(parents=True)
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', 'src/directory:1'))
    assert rules(root, Severity.WARN) == {'spec-pointer'}


def test_run_refreshes_pointer_cache(tmp_path, capsys):
    root = corpus(tmp_path)
    assert run([root], verbose=False) == 0
    (tmp_path / 'src' / 'config.py').write_text('x\n')
    assert run([root], verbose=False) == 0
    assert '[spec-pointer]' in capsys.readouterr().out


def test_non_corpus_file_is_an_input_error(tmp_path):
    path = tmp_path / 'readme.md'
    path.write_text('# Example\n')
    assert run([path], verbose=False) == 2


def test_unlinked_phase_index_cannot_hide_retirement(tmp_path):
    root = corpus(tmp_path)
    phase = root / '1'
    phase.mkdir()
    (phase / 'index.md').write_text(INDEX)
    assert 'spec-index-dangling' in rules(root, Severity.ERROR)
    (root / 'index.md').unlink()
    (root / '01-auth.md').unlink()
    assert run([tmp_path], verbose=False) == 1


def test_multiple_specs_in_one_cell_fail(tmp_path):
    root = corpus(
        tmp_path,
        index=INDEX.replace('[01-auth.md](01-auth.md)', '[Auth](01-auth.md) [Other](02-other.md)'),
    )
    (root / '02-other.md').write_text(SPEC)
    assert 'spec-index-row' in rules(root, Severity.ERROR)


@pytest.mark.parametrize(
    'index',
    [
        '<!--\n' + INDEX + '-->\n',
        INDEX.replace('| [01-auth.md]', '<!--\n| [01-auth.md]') + '-->\n',
        '```md\n' + INDEX + '```\n',
        ''.join('    ' + line + '\n' for line in INDEX.splitlines()),
        INDEX.replace('[01-auth.md](01-auth.md)', '`[01-auth.md](01-auth.md)`'),
        INDEX.replace('[01-auth.md]', r'\[01-auth.md]'),
        INDEX.replace('[01-auth.md]', '![01-auth.md]'),
    ],
)
def test_hidden_or_literal_rows_do_not_register_specs(tmp_path, index):
    root = corpus(tmp_path, index=index)
    assert rules(root, Severity.ERROR) == {'spec-index-row'}


@pytest.mark.parametrize(
    'example',
    [
        '`[Template](02-missing.md)`',
        '``[Template](02-missing.md) with `ticks` ``',
        '<!-- [Template](02-missing.md) -->',
        '```md\n[Template](02-missing.md)\n```',
        '    [Template](02-missing.md)',
        r'\[Template](02-missing.md)',
    ],
)
def test_literal_index_links_do_not_check_targets(tmp_path, example):
    root = corpus(tmp_path, index=INDEX + '\n' + example + '\n')
    assert check_corpus(root) == []


@pytest.mark.parametrize(
    'link',
    [
        '[Auth](<01-auth.md>)',
        "[Auth](01-auth.md 'Example')",
        '[Auth](01-auth.md "Example")',
        '[Auth](01-auth.md (Example))',
        "[Auth](<01-auth.md> 'Example')",
        r'[Auth\|API](01-auth.md)',
        '[Auth](01%2Dauth.md#auth)',
        '[Auth](/specs/01-auth.md)',
        '[Auth][spec]',
    ],
)
def test_index_links_register_specs_and_detect_retirement(tmp_path, link):
    index = INDEX.replace('[01-auth.md](01-auth.md)', link)
    root = corpus(tmp_path, index=index + '\n[spec]: 01-auth.md "Example"\n')
    assert check_corpus(root) == []
    (root / '01-auth.md').unlink()
    found = check_corpus(root)
    assert [item.rule for item in found] == ['spec-index-dangling']
    assert 'index.md:3:' in found[0].message


@pytest.mark.parametrize('link', ['<!-- [Phase](1/index.md) -->', '`[Phase](1/index.md)`'])
def test_hidden_phase_links_do_not_activate_rows(tmp_path, link):
    root = corpus(tmp_path, index=link, name='1/2-webhooks.md')
    (root / '1' / 'index.md').write_text(INDEX.replace('01-auth.md', '2-webhooks.md'))
    assert rules(root, Severity.ERROR) == {'spec-index-row'}


@pytest.mark.parametrize('pointer', ['turn/start', '3/7', 'src/config.py:1\u20132'])
@pytest.mark.xfail(
    strict=True, reason='SPECLINT-POINTER-NOISE-SLASH-TOKENS: slash tokens and en-dash ranges warn'
)
def test_non_file_slash_token_is_not_a_pointer(tmp_path, pointer):
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', pointer))
    assert check_corpus(root) == []
