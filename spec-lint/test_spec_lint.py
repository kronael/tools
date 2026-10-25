# pyright: basic
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from spec_lint import Severity
from spec_lint import check_corpus
from spec_lint import indexed_files
from spec_lint import run
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


SCRIPT = Path(__file__).with_name('spec_lint.py')


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
    """A repo (`.git` file, as a worktree has) holding `app/specs/` plus a
    sibling component `lib/`."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    (tmp_path / '.git').write_text('gitdir: elsewhere\n')
    root = corpus(tmp_path / 'app', spec=spec)
    (tmp_path / 'lib').mkdir()
    (tmp_path / 'lib' / 'shared.py').write_text('X = 1\n')
    return root


def rules(root: Path, severity: Severity) -> set[str]:
    return {item.rule for item in check_corpus(root) if item.severity is severity}


def touch(path: Path) -> None:
    """A file long enough for every line anchor the tests point into it."""
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


def test_tbd_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + '\nRotation interval: TBD.\n')
    assert 'spec-tbd' in rules(root, Severity.ERROR)


def test_tbd_inside_fence_is_ignored(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + '\n```python\n# TODO: upstream bug\n```\n')
    assert check_corpus(root) == []


def test_todo_as_a_file_name_or_a_lowercase_word_passes(tmp_path: Path) -> None:
    root = corpus(
        tmp_path, spec=SPEC + '\nDeferred items go to `TODO.md`; the todo-list renders.\n'
    )
    assert check_corpus(root) == []


def test_nested_fence_does_not_hide_prose(tmp_path: Path) -> None:
    nested = '\n````md\n```\nquoted\n```\n````\n\nRotation interval: TBD.\n'
    root = corpus(tmp_path, spec=SPEC + nested)
    assert 'spec-tbd' in rules(root, Severity.ERROR)


def test_corpus_under_a_generated_dir_name_is_checked(tmp_path: Path) -> None:
    root = corpus(tmp_path / 'build' / 'app', spec=SPEC + '\nRotation interval: TBD.\n')
    assert 'spec-tbd' in rules(root, Severity.ERROR)


def test_status_with_a_yaml_comment_passes(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC.replace('status: shipped', 'status: shipped  # landed'))
    assert check_corpus(root) == []


def test_future_tense_warns(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + '\nWe will move the check into the router.\n')
    assert 'spec-future-tense' in rules(root, Severity.WARN)
    assert 'spec-future-tense' not in rules(root, Severity.ERROR)
    assert run([root], verbose=False) == 0


def test_unresolved_pointer_warns(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', 'src/gone.py:3'))
    found = check_corpus(root)
    assert [item.rule for item in found] == ['spec-pointer']
    assert 'does not resolve under' in found[0].message
    assert run([root], verbose=False) == 0


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


def test_titled_dangling_link_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + '\nSee [the loader](02-loader.md "Loader").\n')
    assert 'spec-link' in rules(root, Severity.ERROR)


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


def test_dangling_body_link_fails(tmp_path: Path) -> None:
    root = corpus(
        tmp_path, spec=SPEC + '\nSee [the loader](02-loader.md) and [app](../src/app.py).\n'
    )
    found = [item for item in check_corpus(root) if item.rule == 'spec-link']
    assert [item.severity for item in found] == [Severity.ERROR, Severity.ERROR]


def test_resolving_scheme_anchor_and_quoted_links_pass(tmp_path: Path) -> None:
    root = corpus(
        tmp_path,
        spec=SPEC + '\nSee [key](../src/config.py), [top](#auth), [btc](asset:btc), '
        '[docs](https://example.test/x), [this](<path>) and the shape `[x](gone.md)`.\n',
    )
    assert check_corpus(root) == []


def test_same_table_in_two_specs_fails(tmp_path: Path) -> None:
    table = '\n```sql\nCREATE TABLE IF NOT EXISTS tokens (id int);\n```\n'
    root = corpus(
        tmp_path, index=INDEX + '| [02-db.md](02-db.md) | shipped | DB |\n', spec=SPEC + table
    )
    (root / '02-db.md').write_text(SPEC + table.replace('IF NOT EXISTS ', ''))
    found = [item for item in check_corpus(root) if item.rule == 'spec-table-owner']
    assert len(found) == 1
    assert found[0].severity is Severity.ERROR
    assert "'tokens' is also declared in 02-db.md" in found[0].message


def test_long_spec_warns_and_a_huge_one_fails(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + 'A line of state.\n' * 500)
    assert 'spec-length' in rules(root, Severity.WARN)
    root = corpus(tmp_path, spec=SPEC + 'A line of state.\n' * 1000)
    assert 'spec-length' in rules(root, Severity.ERROR)


def test_history_framing_warns(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + '\nThe cache is no longer consulted; it used to be.\n')
    found = [item for item in check_corpus(root) if item.rule == 'spec-history']
    assert len(found) == 1
    assert found[0].severity is Severity.WARN
    root = corpus(tmp_path, spec=SPEC + '\nThe cache is read instead of the database.\n')
    assert check_corpus(root) == []


def test_jargon_and_marketing_warn(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + '\nThe test harness is robust.\n')
    found = sorted(item.message for item in check_corpus(root) if item.rule == 'spec-wording')
    assert len(found) == 2
    assert 'say "tests"' in found[0]
    assert 'marketing' in found[1]
    root = corpus(tmp_path, spec=SPEC + '\nThe wallet runs at 3x leverage.\n')
    assert check_corpus(root) == []


def test_options_heading_warns(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + '\n## Option A: cache\n\n## Alternatives\n')
    assert len([item for item in check_corpus(root) if item.rule == 'spec-options']) == 2
    root = corpus(
        tmp_path, spec=SPEC + '\n## Decision\n\nThe cache wins; the one caveat is size.\n'
    )
    assert check_corpus(root) == []


def test_open_questions_outside_draft_warn(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + '\n## Open questions\n\nNone yet.\n')
    assert 'spec-open-questions' in rules(root, Severity.WARN)
    for status in 'draft', 'reference':
        draft = SPEC.replace('shipped', status) + '\n## Open questions\n'
        root = corpus(tmp_path, index=INDEX.replace('shipped', status), spec=draft)
        assert check_corpus(root) == []


def test_checklist_item_warns(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + '\n- [x] wire the router\n- [ ] add the metric\n')
    assert len([item for item in check_corpus(root) if item.rule == 'spec-checklist']) == 2
    root = corpus(tmp_path, spec=SPEC + '\n- the router is wired\n')
    assert check_corpus(root) == []


def test_pointer_past_the_end_warns(tmp_path: Path) -> None:
    for anchor in 'src/config.py:40-52', 'src/config.py:2-999', 'src/config.py:0':
        root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', anchor))
        found = [item for item in check_corpus(root) if item.rule == 'spec-pointer']
        assert len(found) == 1, anchor
        assert 'past the end of the file (3 lines)' in found[0].message
    root = corpus(tmp_path, spec=SPEC.replace('src/config.py:3', 'src/config.py:1-3'))
    assert check_corpus(root) == []


def test_shipped_spec_without_a_file_name_warns(tmp_path: Path) -> None:
    bare = SPEC.replace('`src/config.py:3` holds the key', 'the edge holds the key')
    root = corpus(tmp_path, spec=bare)
    assert 'spec-no-pointer' in rules(root, Severity.WARN)
    root = corpus(tmp_path, spec=bare.replace('the edge', '`config.py`'))
    assert check_corpus(root) == []
    draft = bare.replace('shipped', 'draft')
    root = corpus(tmp_path, index=INDEX.replace('shipped', 'draft'), spec=draft)
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
    root = corpus(tmp_path, spec=SPEC + '\nRotation interval: TBD.\n')
    assert run([root], verbose=True) == 1
    out = capsys.readouterr().out
    assert out.startswith(f'checking {root}\n')
    assert '[spec-tbd]' in out
    assert out.rstrip().endswith('spec-lint: 1 errors, 0 warnings')


def test_help_names_rules_and_exit_codes() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--help'], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert 'spec-pointer' in result.stdout
    assert 'exit codes' in result.stdout


@pytest.mark.usefixtures('locked')
def test_unreadable_dir_is_skipped(tmp_path: Path) -> None:
    root = component_corpus(tmp_path, SPEC.replace('src/config.py:3', 'planning.py:1'))
    touch(tmp_path / 'tools' / 'planning.py')
    assert spec_roots([tmp_path]) == [root]
    assert check_corpus(root) == []


def test_broken_symlink_and_dir_named_like_a_spec_are_not_specs(tmp_path: Path) -> None:
    root = corpus(tmp_path)
    (root / '02-link.md').symlink_to(root / 'gone.md')
    (root / '03-notes.md').mkdir()
    assert check_corpus(root) == []


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
    assert [item.rule for item in check_corpus(root)] == ['spec-no-pointer']


def test_link_with_balanced_parentheses_resolves(tmp_path: Path) -> None:
    root = corpus(tmp_path, spec=SPEC + '\nSee [design](../docs/design(v2).md).\n')
    design = tmp_path / 'docs' / 'design(v2).md'
    design.parent.mkdir()
    design.write_text('# v2\n')
    assert check_corpus(root) == []
    design.unlink()
    found = check_corpus(root)
    assert [item.rule for item in found] == ['spec-link']
    assert "link '../docs/design(v2).md' resolves to nothing" in found[0].message


@pytest.mark.parametrize(
    ('statement', 'plain'),
    [
        ('CREATE TABLE "users" (id int);', 'users'),
        ('CREATE TABLE `users` (id int);', 'users'),
        ('CREATE TABLE [users] (id int);', 'users'),
        ('CREATE TABLE\nusers (id int);', 'users'),
        ('create table if not exists\n  "public"."users" (id int);', 'public.users'),
    ],
)
def test_quoted_or_wrapped_create_table_is_an_owner(
    tmp_path: Path, statement: str, plain: str
) -> None:
    index = INDEX + '| [02-db.md](02-db.md) | shipped | DB |\n'
    root = corpus(tmp_path, index=index, spec=SPEC + f'\n```sql\n-- users\n{statement}\n```\n')
    (root / '02-db.md').write_text(SPEC + f'\n```sql\nCREATE TABLE {plain} (id int);\n```\n')
    found = [item for item in check_corpus(root) if item.rule == 'spec-table-owner']
    assert len(found) == 1
    assert f'01-auth.md:11: [spec-table-owner] table {plain!r} is also declared in 02-db.md' in (
        found[0].message
    )


def test_utf8_spec_reads_and_prints_under_the_c_locale(tmp_path: Path) -> None:
    env = {**os.environ, 'LC_ALL': 'C', 'PYTHONUTF8': '0', 'PYTHONCOERCECLOCALE': '0'}
    for spec, code in (SPEC, 0), (SPEC + '\nRotation interval: TBD.\n', 1):
        root = corpus(tmp_path, spec=spec)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(root)],
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
    quoted = '\n```\n```bash\n# TODO: upstream bug\n```\n\nRotation interval: TBD.\n'
    found = check_corpus(corpus(tmp_path, spec=SPEC + quoted))
    assert [item.rule for item in found] == ['spec-tbd']
    assert "'TBD'" in found[0].message


def test_open_questions_without_a_status_names_the_state(tmp_path: Path) -> None:
    for spec in '# Auth\n\n## Open questions\n', '---\nowner: x\n---\n\n## Open questions\n':
        root = corpus(tmp_path, spec=spec)
        found = [item for item in check_corpus(root) if item.rule == 'spec-open-questions']
        assert len(found) == 1
        assert 'open questions in a spec without a status' in found[0].message


def test_help_and_readme_name_the_same_rules() -> None:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), '--help'], capture_output=True, text=True, check=False
    )
    readme = SCRIPT.with_name('README.md').read_text(encoding='utf-8')
    in_help = set(re.findall(r'^  (spec-[a-z-]+) ', result.stdout, re.MULTILINE))
    in_readme = set(re.findall(r'^\| `(spec-[a-z-]+)` \|', readme, re.MULTILINE))
    assert in_help == in_readme
    assert len(in_help) == 16
    for phrase in 'no frontmatter', 'Status cell is prose':
        assert phrase in result.stdout
    for phrase in 'no YAML frontmatter', 'Status cell that is prose':
        assert phrase in readme
