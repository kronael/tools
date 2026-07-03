import pytest
from pretool_nudge import extract_path
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
    'git push',
    'git reset --hard',
    'git add -A',
    'git add --all',
    'git commit --amend',
    'git commit -m fix --no-verify',
    'rm -rf tmp/build',
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


@pytest.mark.parametrize('command', BLOCK_CASES)
def test_process_blocks_unsafe_commands(command: str) -> None:
    result = process({'tool_name': 'Bash', 'tool_input': {'command': command}})
    assert result is not None
    assert result['decision'] == 'block'
    assert 'unsafe command blocked' in result['reason']


def test_process_blocks_recursive_codex_inside_codex(monkeypatch) -> None:
    monkeypatch.setenv('KRONAEL_IN_CODEX', '1')
    result = process({'tool_name': 'exec_command', 'tool_input': {'cmd': 'codex exec test'}})
    assert result is not None
    assert result['decision'] == 'block'
    assert 'recursive codex' in result['reason']
