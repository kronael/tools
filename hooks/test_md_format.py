from __future__ import annotations

import io
import json
import os
import shutil
import subprocess

import pytest
from md_format import RUMDL_VERSION
from md_format import find_config
from md_format import find_rumdl
from md_format import format_file
from md_format import leftovers
from md_format import main
from md_format import markdown_paths
from md_format import process

PATCH = '*** Begin Patch\n*** Update File: docs/x.md\n+line\n*** Add File: src/y.py\n+pass\n*** Update File: a.md\n*** Move to: docs/b.md\n*** End Patch\n'

PATH_CASES = [
    ({'tool_name': 'Write', 'tool_input': {'file_path': '/repo/README.md'}}, ['/repo/README.md']),
    (
        {'tool_name': 'Edit', 'tool_input': {'file_path': '/repo/docs/a.markdown'}},
        ['/repo/docs/a.markdown'],
    ),
    ({'tool_name': 'MultiEdit', 'tool_input': {'file_path': '/repo/SKILL.MD'}}, ['/repo/SKILL.MD']),
    (
        {'tool_name': 'apply_patch', 'tool_input': {'patch': PATCH}},
        ['docs/x.md', 'a.md', 'docs/b.md'],
    ),
    ({'tool_name': 'apply_patch', 'tool_input': {'patch': 7}}, []),
    ({'tool_name': 'apply_patch', 'tool_input': None}, []),
    ({'tool_name': 'Write', 'tool_input': {'file_path': '/repo/main.py'}}, []),
    ({'tool_name': 'Read', 'tool_input': {'file_path': '/repo/README.md'}}, []),
    ({'tool_name': 'Bash', 'tool_input': {'command': 'touch README.md'}}, []),
    ({'tool_name': 'Write', 'tool_input': {}}, []),
    ({'tool_name': 'Write'}, []),
    ([], []),
    (None, []),
]


@pytest.mark.parametrize(('data', 'expected'), PATH_CASES)
def test_markdown_paths(data, expected) -> None:
    assert markdown_paths(data) == expected


def test_find_config_walks_up(tmp_path) -> None:
    (tmp_path / '.rumdl.toml').write_text('[MD013]\nline-length = 100\n')
    nested = tmp_path / 'docs' / 'deep'
    nested.mkdir(parents=True)
    assert find_config(str(nested)) == str(tmp_path / '.rumdl.toml')


def test_find_config_stops_at_the_repository_root(tmp_path) -> None:
    (tmp_path / '.rumdl.toml').write_text('[MD013]\nline-length = 100\n')
    clone = tmp_path / 'vendor' / 'clone'
    (clone / '.git').mkdir(parents=True)
    (clone / 'docs').mkdir()
    assert find_config(str(clone / 'docs')) is None
    worktree = tmp_path / '.wt'
    worktree.mkdir()
    (worktree / '.git').write_text('gitdir: /elsewhere\n')
    assert find_config(str(worktree)) is None
    (worktree / '.rumdl.toml').write_text('')
    assert find_config(str(worktree)) == str(worktree / '.rumdl.toml')
    assert find_rumdl(str(clone / 'docs'), which=lambda _name: None) is None


def test_find_config_accepts_rumdl_toml(tmp_path) -> None:
    (tmp_path / 'rumdl.toml').write_text('')
    assert find_config(str(tmp_path)) == str(tmp_path / 'rumdl.toml')


@pytest.mark.parametrize(
    ('pyproject', 'found'),
    [
        ('[project]\nname = "x"\n\n[tool.rumdl]\nline-length = 100\n', True),
        ('[tool.rumdl.MD013]\nline-length = 100\n', True),
        ('  [tool.rumdl]\n', True),
        ('[project]\nname = "x"\n', False),
        ('# [tool.rumdl]\nname = "x"\n', False),
        ('[tool.rumdlx]\n', False),
        ('description = "see [tool.rumdl]"\n', False),
    ],
)
def test_find_config_reads_the_pyproject_section_by_line(tmp_path, pyproject, found) -> None:
    (tmp_path / 'pyproject.toml').write_text(pyproject)
    expected = str(tmp_path / 'pyproject.toml') if found else None
    assert find_config(str(tmp_path)) == expected


def test_find_config_none_outside_a_configured_tree(tmp_path) -> None:
    assert find_config(str(tmp_path)) is None


def test_find_rumdl_prefers_the_repo_pin(tmp_path) -> None:
    binary = tmp_path / 'node_modules' / '.bin' / 'rumdl'
    binary.parent.mkdir(parents=True)
    binary.write_text('#!/bin/sh\n')
    binary.chmod(0o755)
    nested = tmp_path / 'docs'
    nested.mkdir()
    assert find_rumdl(str(nested), which=lambda name: f'/usr/bin/{name}') == [str(binary)]


def test_find_rumdl_does_not_cross_into_a_nested_repository(tmp_path) -> None:
    binary = tmp_path / 'node_modules' / '.bin' / 'rumdl'
    binary.parent.mkdir(parents=True)
    binary.write_text('#!/bin/sh\n')
    binary.chmod(0o755)
    clone = tmp_path / 'clone'
    (clone / '.git').mkdir(parents=True)
    assert find_rumdl(str(clone), which=lambda _name: None) is None


def test_find_rumdl_falls_back_to_path_then_uvx(tmp_path) -> None:
    assert find_rumdl(
        str(tmp_path), which=lambda name: '/usr/bin/rumdl' if name == 'rumdl' else None
    ) == ['/usr/bin/rumdl']
    assert find_rumdl(
        str(tmp_path), which=lambda name: '/usr/bin/uvx' if name == 'uvx' else None
    ) == [
        'uvx',
        f'rumdl@{RUMDL_VERSION}',
    ]
    assert find_rumdl(str(tmp_path), which=lambda _name: None) is None


def test_find_rumdl_ignores_a_non_executable_pin(tmp_path) -> None:
    binary = tmp_path / 'node_modules' / '.bin' / 'rumdl'
    binary.parent.mkdir(parents=True)
    binary.write_text('')
    binary.chmod(0o644)
    assert find_rumdl(str(tmp_path), which=lambda _name: None) is None


def test_leftovers_are_the_unfixed_findings() -> None:
    output = (
        'a.md:4:101: [MD013] Line length 132 exceeds 100 characters\n'
        'a.md:7:1: [MD013] Line length exceeds 100 characters [fixed]\n'
        'a.md:7:132: [MD009] Trailing space found [fixed]\n'
        '\n'
        'Fixed: 2/3 issues in 1 file (74ms)\n'
    )
    assert leftovers(output) == ['a.md:4:101: [MD013] Line length 132 exceeds 100 characters']
    assert leftovers('Success: No issues found in 1 file (10ms)\n') == []


def completed(
    stdout: str = '', returncode: int = 0, stderr: str = ''
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=returncode, stdout=stdout, stderr=stderr)


def test_format_file_runs_rumdl_in_the_file_directory_and_reports_a_change(tmp_path) -> None:
    doc = tmp_path / 'docs' / 'a.md'
    doc.parent.mkdir()
    doc.write_text('long line\n')
    calls = []

    def run(argv, **kwargs):
        calls.append(
            (
                argv,
                kwargs['cwd'],
                kwargs['encoding'],
                kwargs['errors'],
                kwargs['env']['RUMDL_OUTPUT_FORMAT'],
            )
        )
        doc.write_text('long\nline\n')
        return completed('a.md:1:1: [MD013] Line length exceeds 100 characters [fixed]\n')

    note = format_file(str(doc), ['/bin/rumdl'], run=run)
    assert calls == [
        (
            ['/bin/rumdl', '--color', 'never', 'fmt', '--', 'a.md'],
            str(doc.parent),
            'utf-8',
            'replace',
            'text',
        )
    ]
    assert note == 'rumdl reformatted a.md; Read it again before the next Edit.'


def test_format_file_is_silent_when_nothing_changed(tmp_path) -> None:
    doc = tmp_path / 'a.md'
    doc.write_text('fine\n')
    assert (
        format_file(str(doc), ['/bin/rumdl'], run=lambda *_a, **_k: completed('Success\n')) is None
    )


def test_format_file_reports_what_rumdl_could_not_fix(tmp_path) -> None:
    doc = tmp_path / 'a.md'
    doc.write_text('fine\n')
    output = 'a.md:4:101: [MD013] Line length 132 exceeds 100 characters\n'
    note = format_file(str(doc), ['/bin/rumdl'], run=lambda *_a, **_k: completed(output))
    assert note == 'rumdl could not fix: a.md:4:101: [MD013] Line length 132 exceeds 100 characters'


def test_format_file_reports_a_non_zero_exit_with_its_last_line(tmp_path) -> None:
    doc = tmp_path / 'a.md'
    doc.write_text('fine\n')
    failed = completed(returncode=2, stderr='Error: Failed to parse .rumdl.toml\n\n')
    note = format_file(str(doc), ['/bin/rumdl'], run=lambda *_a, **_k: failed)
    assert note == 'rumdl exited 2 on a.md: Error: Failed to parse .rumdl.toml'


def test_format_file_reports_a_failed_run(tmp_path) -> None:
    doc = tmp_path / 'a.md'
    doc.write_text('fine\n')

    def run(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd='rumdl', timeout=20)

    note = format_file(str(doc), ['/bin/rumdl'], run=run)
    assert note is not None
    assert note.startswith('rumdl failed on a.md:')


def test_format_file_keeps_the_reread_note_when_rumdl_times_out_after_the_rewrite(tmp_path) -> None:
    doc = tmp_path / 'a.md'
    doc.write_text('long line\n')

    def run(*_args, **_kwargs):
        doc.write_text('long\nline\n')
        raise subprocess.TimeoutExpired(cmd='rumdl', timeout=20)

    note = format_file(str(doc), ['/bin/rumdl'], run=run)
    assert note is not None
    assert note.startswith(
        'rumdl reformatted a.md; Read it again before the next Edit. rumdl failed on a.md:'
    )


def write_payload(path: str) -> dict:
    return {'tool_name': 'Write', 'tool_input': {'file_path': path}}


def test_process_is_silent_outside_a_configured_repo() -> None:
    calls = []
    result = process(
        write_payload('/repo/README.md'),
        find_config_fn=lambda _directory: None,
        find_rumdl_fn=lambda _directory: calls.append('rumdl') or ['/bin/rumdl'],
        format_fn=lambda _path, _command: calls.append('fmt') or 'changed',
        is_file_fn=lambda _path: True,
    )
    assert result is None
    assert calls == []


def test_process_is_silent_for_a_non_markdown_write() -> None:
    result = process(
        write_payload('/repo/main.py'),
        find_config_fn=lambda _directory: '/repo/.rumdl.toml',
        find_rumdl_fn=lambda _directory: ['/bin/rumdl'],
        format_fn=lambda _path, _command: 'changed',
        is_file_fn=lambda _path: True,
    )
    assert result is None


def test_process_emits_the_formatter_note_as_post_tool_context() -> None:
    seen = []

    def fmt(path, command):
        seen.append((path, command))
        return 'rumdl reformatted README.md; Read it again before the next Edit.'

    result = process(
        write_payload('/repo/README.md'),
        find_config_fn=lambda _directory: '/repo/.rumdl.toml',
        find_rumdl_fn=lambda _directory: ['/repo/node_modules/.bin/rumdl'],
        format_fn=fmt,
        is_file_fn=lambda _path: True,
    )
    assert seen == [('/repo/README.md', ['/repo/node_modules/.bin/rumdl'])]
    assert result == {
        'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': 'rumdl reformatted README.md; Read it again before the next Edit.',
        },
    }


def test_process_formats_every_markdown_file_of_a_patch() -> None:
    seen = []
    result = process(
        {'tool_name': 'apply_patch', 'tool_input': {'patch': PATCH}},
        find_config_fn=lambda _directory: '/repo/.rumdl.toml',
        find_rumdl_fn=lambda _directory: ['/bin/rumdl'],
        format_fn=lambda path, _command: seen.append(path) or f'{os.path.basename(path)} done.',
        is_file_fn=lambda _path: True,
    )
    assert seen == ['docs/x.md', 'a.md', 'docs/b.md']
    assert result is not None
    assert result['hookSpecificOutput']['additionalContext'] == 'x.md done. a.md done. b.md done.'


def test_process_skips_a_path_the_tool_removed() -> None:
    seen = []
    result = process(
        {'tool_name': 'apply_patch', 'tool_input': {'patch': PATCH}},
        find_config_fn=lambda _directory: '/repo/.rumdl.toml',
        find_rumdl_fn=lambda _directory: ['/bin/rumdl'],
        format_fn=lambda path, _command: seen.append(path) or None,
        is_file_fn=lambda path: path != 'a.md',
    )
    assert seen == ['docs/x.md', 'docs/b.md']
    assert result is None


def test_process_resolves_a_relative_payload_path_against_the_cwd(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'docs').mkdir()
    (tmp_path / 'docs' / 'a.md').write_text('x\n')
    asked = []
    process(
        write_payload('docs/a.md'),
        find_config_fn=lambda directory: asked.append(directory) or None,
        find_rumdl_fn=lambda _directory: ['/bin/rumdl'],
        format_fn=lambda _path, _command: None,
    )
    assert asked == [str(tmp_path / 'docs')]


def test_process_is_silent_when_the_formatter_had_nothing_to_say() -> None:
    result = process(
        write_payload('/repo/README.md'),
        find_config_fn=lambda _directory: '/repo/.rumdl.toml',
        find_rumdl_fn=lambda _directory: ['/bin/rumdl'],
        format_fn=lambda _path, _command: None,
        is_file_fn=lambda _path: True,
    )
    assert result is None


def test_process_names_the_missing_formatter_in_a_configured_repo() -> None:
    result = process(
        write_payload('/repo/docs/a.md'),
        find_config_fn=lambda _directory: '/repo/.rumdl.toml',
        find_rumdl_fn=lambda _directory: None,
        format_fn=lambda _path, _command: pytest.fail('must not run without a binary'),
        is_file_fn=lambda _path: True,
    )
    assert result is not None
    text = result['hookSpecificOutput']['additionalContext']
    assert text.startswith('a.md is under a rumdl config but no rumdl is installed')
    assert 'make prepare' in text


def test_process_resolves_the_config_from_the_file_directory() -> None:
    asked = []
    process(
        write_payload('/repo/docs/deep/a.md'),
        find_config_fn=lambda directory: asked.append(directory) or None,
        find_rumdl_fn=lambda _directory: ['/bin/rumdl'],
        format_fn=lambda _path, _command: None,
        is_file_fn=lambda _path: True,
    )
    assert asked == [os.path.abspath('/repo/docs/deep')]


@pytest.mark.parametrize('raw', ['', '{bad json', '[]', 'null', '{"tool_name": null}'])
def test_main_stays_silent_on_malformed_or_foreign_payloads(monkeypatch, capsys, raw) -> None:
    monkeypatch.setattr('sys.stdin', io.StringIO(raw))
    main()
    assert capsys.readouterr().out == ''


def test_main_runs_the_repo_pin_and_prints_the_context_as_one_json_line(
    tmp_path, monkeypatch, capsys
) -> None:
    (tmp_path / '.rumdl.toml').write_text('[MD013]\nline-length = 100\n')
    binary = tmp_path / 'node_modules' / '.bin' / 'rumdl'
    binary.parent.mkdir(parents=True)
    binary.write_text(
        '#!/bin/sh\nfor last; do :; done\nprintf "wrapped\\n" > "$last"\n'
        'echo "$last:1:1: [MD013] Line length exceeds 100 characters [fixed]"\n'
    )
    binary.chmod(0o755)
    doc = tmp_path / 'docs' / 'a.md'
    doc.parent.mkdir()
    doc.write_text('a long line\n')
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(write_payload(str(doc)))))
    main()
    out = capsys.readouterr().out
    assert doc.read_text() == 'wrapped\n'
    assert json.loads(out) == {
        'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': 'rumdl reformatted a.md; Read it again before the next Edit.',
        },
    }


@pytest.mark.skipif(
    not (os.environ.get('RUMDL_BIN') or shutil.which('rumdl')),
    reason='needs a rumdl binary: RUMDL_BIN=<path> or rumdl on PATH',
)
def test_pinned_rumdl_prints_the_line_shape_the_hook_parses(tmp_path) -> None:
    binary = os.environ.get('RUMDL_BIN') or shutil.which('rumdl')
    assert binary is not None
    (tmp_path / '.rumdl.toml').write_text('[MD013]\nline-length = 100\nreflow = true\n')
    doc = tmp_path / 'a.md'
    doc.write_text('# T\n\n' + 'word ' * 40 + '\n')
    note = format_file(str(doc), [binary])
    assert note == 'rumdl reformatted a.md; Read it again before the next Edit.'
    assert max(len(line) for line in doc.read_text().splitlines()) <= 100
    doc.write_text('no heading\n')
    note = format_file(str(doc), [binary])
    assert note is not None
    assert note.startswith('rumdl could not fix: a.md:1:1: [MD041]')
    assert format_file(str(tmp_path / 'missing.md'), [binary]) == (
        'rumdl exited 2 on missing.md: Error: Failed to find markdown files: File not found: missing.md'
    )
