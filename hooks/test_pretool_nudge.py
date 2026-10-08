from __future__ import annotations

import io
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest
from pretool_nudge import extract_path
from pretool_nudge import format_markdown
from pretool_nudge import main
from pretool_nudge import process
from pretool_nudge import skill_for

HOOKS_DIR = Path(__file__).resolve().parent
LONG_LINE = '# Title\n\n' + 'word ' * 40 + '\n'

SKILL_CASES = [
    ('foo.go', '/go'),
    ('foo.rs', '/rs'),
    ('foo.py', '/py'),
    ('foo.ts', '/ts'),
    ('foo.tsx', '/tsx'),
    ('foo.sql', '/sql'),
    ('foo.sh', '/sh'),
    ('foo.bash', '/sh'),
    ('foo.zsh', '/sh'),
    ('foo.html', '/htmx'),
    ('foo.htm', '/htmx'),
    ('tmpl.jinja', '/htmx'),
    ('tmpl.j2', '/htmx'),
    ('live.heex', '/htmx'),
    ('Makefile', '/mk'),
    ('GnuMakefile', '/mk'),
    ('build.mk', '/mk'),
    ('build.make', '/mk'),
    ('MAKEFILE', '/mk'),
    ('Dockerfile', '/ops'),
    ('Dockerfile.dev', '/ops'),
    ('Dockerfile.prod', '/ops'),
    ('docker-compose.yml', '/ops'),
    ('docker-compose.yaml', '/ops'),
    ('compose.yml', '/ops'),
    ('compose.yaml', '/ops'),
    ('/repo/.github/workflows/ci.yml', '/ops'),
    ('.github/workflows/ci.yml', '/ops'),
    ('/srv/ansible/playbook.yml', '/ops'),
    ('vault.ansible.yml', '/ops'),
    ('app.service', '/ops'),
    ('cron.timer', '/ops'),
    ('proxy.socket', '/ops'),
    ('SKILL.md', '/wisdom'),
    ('/repo/CLAUDE.md', '/wisdom'),
    ('AGENTS.md', '/wisdom'),
    ('foo.xyz', None),
    ('foo', None),
    ('README', None),
    ('', None),
]

PATH_CASES = [
    ({'tool_input': {'file_path': '/x.py'}}, '/x.py'),
    ({'tool_input': {'notebook_path': '/n.ipynb'}}, '/n.ipynb'),
    ({'tool_input': {'file_path': '/x.py', 'notebook_path': '/n.ipynb'}}, '/x.py'),
    ({'tool_input': None}, ''),
    ({'tool_input': 'not-a-dict'}, ''),
    ({'tool_input': {}}, ''),
    ({'tool_input': {'file_path': None}}, ''),
    (
        {
            'tool_name': 'apply_patch',
            'tool_input': {
                'patch': '*** Begin Patch\n*** Update File: src/app.py\n@@\n',
            },
        },
        'src/app.py',
    ),
    (
        {
            'tool_name': 'apply_patch',
            'tool_input': {
                'patch': '*** Begin Patch\n*** Add File: Dockerfile\n+FROM scratch\n',
            },
        },
        'Dockerfile',
    ),
    ({'tool_name': 'apply_patch', 'tool_input': {'patch': 'not a patch'}}, ''),
    ({}, ''),
    (None, ''),
    ('not-a-dict', ''),
]

PROCESS_CASES = [
    ({'tool_name': 'Read', 'tool_input': {'file_path': '/x.py'}}, '/py'),
    ({'tool_name': 'Edit', 'tool_input': {'file_path': '/x.go'}}, '/go'),
    ({'tool_name': 'Write', 'tool_input': {'file_path': '/x.rs'}}, '/rs'),
    ({'tool_name': 'MultiEdit', 'tool_input': {'file_path': '/x.tsx'}}, '/tsx'),
    ({'tool_name': 'NotebookEdit', 'tool_input': {'notebook_path': '/n.py'}}, '/py'),
    (
        {
            'tool_name': 'apply_patch',
            'tool_input': {'patch': '*** Begin Patch\n*** Update File: /x.py\n'},
        },
        '/py',
    ),
    ({'tool_name': 'Bash', 'tool_input': {'file_path': '/x.py'}}, None),
    ({'tool_name': 'Read'}, None),
    ({'tool_name': 'Read', 'tool_input': {'file_path': '/x.xyz'}}, None),
    ({'tool_name': None, 'tool_input': {'file_path': '/x.py'}}, None),
    ({}, None),
    ([], None),
    (None, None),
]

BLOCK_CASES = [
    'git reset --hard',
    'git add -A',
    'git add --all',
    'git commit --amend',
    'git commit -m fix --no-verify',
    'git commit -m "fix\n\nCo-Authored-By: A <a@b.c>"',
    'git merge --squash feature',
    'git rebase -i HEAD~3',
    'git checkout -b feature',
    'git switch -c feature',
    'git worktree add /repo/.wt origin/master',
    'killall node',
    'rm -rf tmp/build',
]

NONBLOCK_CASES = [
    'git push',
    'git commit -m "normal message"',
    'git merge origin/master',
    'git rebase origin/master',
    'git checkout master',
    'git checkout -- file.py',
    'git worktree add --detach /repo/.wt origin/master',
    'git status',
]


@pytest.mark.parametrize(
    ('path', 'skill'), SKILL_CASES, ids=[c[0] or '<empty>' for c in SKILL_CASES]
)
def test_skill_for(path: str, skill: str | None) -> None:
    assert skill_for(path) == skill


@pytest.mark.parametrize(('payload', 'path'), PATH_CASES)
def test_extract_path(payload: object, path: str) -> None:
    assert extract_path(payload) == path


@pytest.mark.parametrize(('payload', 'expected_skill'), PROCESS_CASES)
def test_process(payload: object, expected_skill: str | None) -> None:
    result = process(payload)
    if expected_skill is None:
        assert result is None
    else:
        assert result is not None
        assert result['hookSpecificOutput']['hookEventName'] == 'PreToolUse'
        context = result['hookSpecificOutput']['additionalContext']
        assert f'follow {expected_skill} conventions.' in context


@pytest.mark.parametrize(('path', 'skill'), SKILL_CASES)
def test_process_names_code_md_for_code_skills(path: str, skill: str | None) -> None:
    result = process({'tool_name': 'Edit', 'tool_input': {'file_path': path}})
    if skill is None:
        assert result is None
        return
    context = result['hookSpecificOutput']['additionalContext']
    named = 'software/code.md' in context
    assert named == (skill not in ('/ops', '/wisdom'))


@pytest.mark.parametrize('command', BLOCK_CASES)
def test_process_blocks_unsafe_commands(command: str) -> None:
    result = process({'tool_name': 'Bash', 'tool_input': {'command': command}})
    assert result is not None
    assert result['decision'] == 'block'
    assert 'unsafe command blocked' in result['reason']


@pytest.mark.parametrize('command', NONBLOCK_CASES)
def test_process_allows_safe_commands(command: str) -> None:
    assert process({'tool_name': 'Bash', 'tool_input': {'command': command}}) is None


def test_process_blocks_recursive_codex_inside_codex() -> None:
    result = process(
        {'tool_name': 'exec_command', 'tool_input': {'cmd': 'codex exec test'}, 'harness': 'codex'}
    )
    assert result is not None
    assert result['decision'] == 'block'
    assert 'recursive codex' in result['reason']


@pytest.mark.parametrize(
    'command',
    [
        'rm -r build',
        'rm -R build',
        'rm --recursive build',
        'sudo rm -r /srv/x',
        'echo done && rm -r tmp',
    ],
)
def test_process_blocks_recursive_removal_without_force(command: str) -> None:
    """Recursive removal deletes a tree with or without -f, so -r alone blocks."""
    result = process({'tool_name': 'Bash', 'tool_input': {'command': command}})
    assert result is not None, command
    assert result['decision'] == 'block'


@pytest.mark.parametrize(
    'command', ['rm -f stale.log', 'rm -i x', 'grep -r pat .', 'charm --version']
)
def test_process_allows_nonrecursive_and_lookalikes(command: str) -> None:
    assert process({'tool_name': 'Bash', 'tool_input': {'command': command}}) is None


def test_main_blocks_every_time_not_only_once(tmp_path, monkeypatch, capsys) -> None:
    """A block is a ban, not a nudge: the dedup cache must never swallow it.

    A Bash call carries no file path, so every one shares a single dedup key.
    Routing blocks through that cache disarmed the ban after the first hit.
    """
    monkeypatch.setenv('HOME', str(tmp_path))
    payload = json.dumps(
        {
            'tool_name': 'Bash',
            'session_id': 'same-session',
            'tool_input': {'command': 'rm -r build'},
        }
    )
    for attempt in range(3):
        monkeypatch.setattr('sys.stdin', io.StringIO(payload))
        main()
        assert '"block"' in capsys.readouterr().out, f'attempt {attempt + 1} not blocked'


def opted_in_repo(root: Path, rumdl_script: str = 'printf "wrapped\\n" > "$3"\n') -> Path:
    """A repository root with `.rumdl.toml` and a pinned fake rumdl; `$3` is the
    file `rumdl fmt -- <file>` names."""
    (root / '.git').mkdir()
    (root / '.rumdl.toml').write_text('[MD013]\nline-length = 100\nreflow = true\n')
    binary = root / 'node_modules' / '.bin' / 'rumdl'
    binary.parent.mkdir(parents=True)
    binary.write_text('#!/bin/sh\n' + rumdl_script)
    binary.chmod(0o755)
    doc = root / 'docs' / 'a.md'
    doc.parent.mkdir()
    doc.write_text(LONG_LINE)
    return doc


def post_tool_payload(path: Path, tool_name: str = 'Write') -> dict:
    return {
        'hook_event_name': 'PostToolUse',
        'tool_name': tool_name,
        'tool_input': {'file_path': str(path)},
    }


def test_format_markdown_runs_the_pin_from_the_root_and_stays_silent(tmp_path) -> None:
    doc = opted_in_repo(tmp_path, 'printf "%s|%s\\n" "$PWD" "$*" > "$3"\n')
    assert format_markdown(post_tool_payload(doc, 'Edit')) is None
    assert doc.read_text() == f'{os.path.realpath(tmp_path)}|fmt -- docs/a.md\n'


@pytest.mark.skipif(shutil.which('rumdl') is None, reason='rumdl is not on PATH')
def test_format_markdown_wraps_a_long_line_with_the_real_rumdl(tmp_path) -> None:
    doc = opted_in_repo(tmp_path)
    (tmp_path / 'node_modules' / '.bin' / 'rumdl').unlink()
    assert format_markdown(post_tool_payload(doc)) is None
    text = doc.read_text()
    assert text.startswith('# Title\n\n')
    assert max(len(line) for line in text.splitlines()) <= 100


@pytest.mark.parametrize(
    'case', ['python file', 'read tool', 'no config', 'no repository', 'nested clone']
)
def test_format_markdown_leaves_a_file_alone_unless_its_repo_opted_in(tmp_path, case) -> None:
    doc = opted_in_repo(tmp_path)
    payload = post_tool_payload(doc)
    if case == 'python file':
        doc = doc.with_suffix('.py')
        doc.write_text(LONG_LINE)
        payload = post_tool_payload(doc)
    elif case == 'read tool':
        payload = post_tool_payload(doc, 'Read')
    elif case == 'no config':
        (tmp_path / '.rumdl.toml').unlink()
    elif case == 'no repository':
        (tmp_path / '.git').rmdir()
    elif case == 'nested clone':
        clone = tmp_path / 'vendor' / 'clone'
        (clone / '.git').mkdir(parents=True)
        doc = clone / 'README.md'
        doc.write_text(LONG_LINE)
        payload = post_tool_payload(doc)
    assert format_markdown(payload) is None
    assert doc.read_text() == LONG_LINE


def test_format_markdown_reports_a_failed_rumdl_in_one_line(tmp_path) -> None:
    doc = opted_in_repo(tmp_path, 'echo "Config error: bad .rumdl.toml" >&2\nexit 2\n')
    result = format_markdown(post_tool_payload(doc))
    assert result == {
        'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': 'rumdl exited 2 on docs/a.md: Config error: bad .rumdl.toml',
        },
    }
    assert doc.read_text() == LONG_LINE


def test_format_markdown_puts_the_written_bytes_back_after_a_timeout(tmp_path, monkeypatch) -> None:
    doc = opted_in_repo(tmp_path, 'printf "half" > "$3"\nsleep 5\n')
    monkeypatch.setattr('pretool_nudge.RUMDL_TIMEOUT_S', 1.0)
    result = format_markdown(post_tool_payload(doc))
    assert result is not None
    assert result['hookSpecificOutput']['additionalContext'].startswith(
        'rumdl failed on docs/a.md:'
    )
    assert doc.read_text() == LONG_LINE


def test_format_markdown_names_a_missing_rumdl(tmp_path, monkeypatch) -> None:
    doc = opted_in_repo(tmp_path)
    (tmp_path / 'node_modules' / '.bin' / 'rumdl').unlink()
    monkeypatch.setenv('PATH', str(tmp_path / 'empty-path'))
    result = format_markdown(post_tool_payload(doc))
    assert result == {
        'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': 'rumdl is not installed; docs/a.md was not reflowed.',
        },
    }
    assert doc.read_text() == LONG_LINE


def test_main_routes_post_tool_use_to_the_formatter_only(tmp_path, monkeypatch, capsys) -> None:
    doc = opted_in_repo(tmp_path)
    monkeypatch.setenv('HOME', str(tmp_path))
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(post_tool_payload(doc))))
    main()
    assert capsys.readouterr().out == ''
    assert doc.read_text() == 'wrapped\n'

    script = tmp_path / 'x.py'
    script.write_text('pass\n')
    for event, nudged in (('PostToolUse', False), ('PreToolUse', True)):
        payload = {**post_tool_payload(script), 'hook_event_name': event}
        monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(payload)))
        main()
        assert ('follow /py conventions' in capsys.readouterr().out) is nudged, event


def run_post_tool_nudge(tmp_path: Path, doc: Path) -> subprocess.CompletedProcess[str]:
    """The bash entry resolves ~/.claude/hooks, so a fake home links there."""
    home = tmp_path / 'home'
    (home / '.claude').mkdir(parents=True)
    (home / '.claude' / 'hooks').symlink_to(HOOKS_DIR)
    return subprocess.run(
        ['bash', str(HOOKS_DIR / 'post_tool_nudge.sh')],
        input=json.dumps(post_tool_payload(doc)),
        capture_output=True,
        text=True,
        cwd=doc.parent,
        env={'HOME': str(home), 'PATH': '/usr/bin:/bin'},
        check=False,
    )


def test_post_tool_nudge_feeds_a_markdown_write_through_the_installed_hook(tmp_path) -> None:
    repo = tmp_path / 'repo'
    repo.mkdir()
    doc = opted_in_repo(repo)
    run = run_post_tool_nudge(tmp_path, doc)
    assert (run.returncode, run.stdout, run.stderr) == (0, '', '')
    assert doc.read_text() == 'wrapped\n'


def test_post_tool_nudge_prints_a_note_as_its_only_output(tmp_path) -> None:
    repo = tmp_path / 'repo'
    repo.mkdir()
    doc = opted_in_repo(repo, 'echo "Config error: bad .rumdl.toml" >&2\nexit 2\n')
    run = run_post_tool_nudge(tmp_path, doc)
    assert (run.returncode, run.stderr) == (0, '')
    assert json.loads(run.stdout) == {
        'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': 'rumdl exited 2 on docs/a.md: Config error: bad .rumdl.toml',
        },
    }
    assert doc.read_text() == LONG_LINE
