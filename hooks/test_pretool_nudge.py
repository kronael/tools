from __future__ import annotations

import io
import json

import pytest
from pretool_nudge import extract_path
from pretool_nudge import main
from pretool_nudge import process
from pretool_nudge import skill_for

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
