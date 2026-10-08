from __future__ import annotations

import io
import json
import os
import subprocess

import pytest
from md_format import RUMDL_VERSION
from md_format import find_config
from md_format import find_rumdl
from md_format import format_file
from md_format import leftovers
from md_format import main
from md_format import markdown_path
from md_format import process

PATH_CASES = [
    ({'tool_name': 'Write', 'tool_input': {'file_path': '/repo/README.md'}}, '/repo/README.md'),
    (
        {'tool_name': 'Edit', 'tool_input': {'file_path': '/repo/docs/a.markdown'}},
        '/repo/docs/a.markdown',
    ),
    ({'tool_name': 'MultiEdit', 'tool_input': {'file_path': '/repo/SKILL.MD'}}, '/repo/SKILL.MD'),
    (
        {'tool_name': 'apply_patch', 'tool_input': {'patch': '*** Update File: docs/x.md\n+line'}},
        'docs/x.md',
    ),
    ({'tool_name': 'Write', 'tool_input': {'file_path': '/repo/main.py'}}, None),
    ({'tool_name': 'Read', 'tool_input': {'file_path': '/repo/README.md'}}, None),
    ({'tool_name': 'Bash', 'tool_input': {'command': 'touch README.md'}}, None),
    ({'tool_name': 'Write', 'tool_input': {}}, None),
    ({'tool_name': 'Write'}, None),
    ([], None),
    (None, None),
]


@pytest.mark.parametrize(('data', 'expected'), PATH_CASES)
def test_markdown_path(data, expected) -> None:
    assert markdown_path(data) == expected


def test_find_config_walks_up(tmp_path) -> None:
    (tmp_path / '.rumdl.toml').write_text('[MD013]\nline-length = 100\n')
    nested = tmp_path / 'docs' / 'deep'
    nested.mkdir(parents=True)
    assert find_config(str(nested)) == str(tmp_path / '.rumdl.toml')


def test_find_config_accepts_rumdl_toml_and_pyproject_section(tmp_path) -> None:
    plain = tmp_path / 'plain'
    plain.mkdir()
    (plain / 'rumdl.toml').write_text('')
    assert find_config(str(plain)) == str(plain / 'rumdl.toml')
    py = tmp_path / 'py'
    py.mkdir()
    (py / 'pyproject.toml').write_text('[project]\nname = "x"\n\n[tool.rumdl]\nline-length = 100\n')
    assert find_config(str(py)) == str(py / 'pyproject.toml')
    bare = tmp_path / 'bare'
    bare.mkdir()
    (bare / 'pyproject.toml').write_text('[project]\nname = "x"\n')
    assert find_config(str(bare)) is None


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


def completed(stdout: str = '') -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=[], returncode=0, stdout=stdout, stderr='')


def test_format_file_runs_rumdl_in_the_file_directory_and_reports_a_change(tmp_path) -> None:
    doc = tmp_path / 'docs' / 'a.md'
    doc.parent.mkdir()
    doc.write_text('long line\n')
    calls = []

    def run(argv, **kwargs):
        calls.append((argv, kwargs['cwd']))
        doc.write_text('long\nline\n')
        return completed('a.md:1:1: [MD013] Line length exceeds 100 characters [fixed]\n')

    note = format_file(str(doc), ['/bin/rumdl'], run=run)
    assert calls == [(['/bin/rumdl', 'fmt', 'a.md'], str(doc.parent))]
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


def test_format_file_reports_a_failed_run(tmp_path) -> None:
    doc = tmp_path / 'a.md'
    doc.write_text('fine\n')

    def run(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd='rumdl', timeout=20)

    note = format_file(str(doc), ['/bin/rumdl'], run=run)
    assert note is not None
    assert note.startswith('rumdl failed on a.md:')


def write_payload(path: str) -> dict:
    return {'tool_name': 'Write', 'tool_input': {'file_path': path}}


def test_process_is_silent_outside_a_configured_repo() -> None:
    calls = []
    result = process(
        write_payload('/repo/README.md'),
        config=lambda _directory: None,
        rumdl=lambda _directory: calls.append('rumdl') or ['/bin/rumdl'],
        fmt=lambda _path, _command: calls.append('fmt') or 'changed',
    )
    assert result is None
    assert calls == []


def test_process_is_silent_for_a_non_markdown_write() -> None:
    result = process(
        write_payload('/repo/main.py'),
        config=lambda _directory: '/repo/.rumdl.toml',
        rumdl=lambda _directory: ['/bin/rumdl'],
        fmt=lambda _path, _command: 'changed',
    )
    assert result is None


def test_process_emits_the_formatter_note_as_post_tool_context() -> None:
    seen = []

    def fmt(path, command):
        seen.append((path, command))
        return 'rumdl reformatted README.md; Read it again before the next Edit.'

    result = process(
        write_payload('/repo/README.md'),
        config=lambda _directory: '/repo/.rumdl.toml',
        rumdl=lambda _directory: ['/repo/node_modules/.bin/rumdl'],
        fmt=fmt,
    )
    assert seen == [('/repo/README.md', ['/repo/node_modules/.bin/rumdl'])]
    assert result == {
        'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': 'rumdl reformatted README.md; Read it again before the next Edit.',
        },
    }


def test_process_is_silent_when_the_formatter_had_nothing_to_say() -> None:
    result = process(
        write_payload('/repo/README.md'),
        config=lambda _directory: '/repo/.rumdl.toml',
        rumdl=lambda _directory: ['/bin/rumdl'],
        fmt=lambda _path, _command: None,
    )
    assert result is None


def test_process_names_the_missing_formatter_in_a_configured_repo() -> None:
    result = process(
        write_payload('/repo/docs/a.md'),
        config=lambda _directory: '/repo/.rumdl.toml',
        rumdl=lambda _directory: None,
        fmt=lambda _path, _command: pytest.fail('must not run without a binary'),
    )
    assert result is not None
    text = result['hookSpecificOutput']['additionalContext']
    assert text.startswith('a.md is under a rumdl config but no rumdl is installed')
    assert 'make prepare' in text


def test_process_resolves_the_config_from_the_file_directory() -> None:
    asked = []
    process(
        write_payload('/repo/docs/deep/a.md'),
        config=lambda directory: asked.append(directory) or None,
        rumdl=lambda _directory: ['/bin/rumdl'],
        fmt=lambda _path, _command: None,
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
        '#!/bin/sh\nprintf "wrapped\\n" > "$2"\necho "$2:1:1: [MD013] Line length exceeds 100 characters [fixed]"\n'
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
