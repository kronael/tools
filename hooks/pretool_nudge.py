#!/usr/bin/env python3
# PreToolUse hook: emit a per-language skill nudge based on file extension.
# Production: silent-fail on any error (NEVER block a tool call). Tests:
# `pytest hooks/pretool_nudge.py` or `make test`.
import contextlib
import json
import os
import sys
import tempfile

TOOLS_OF_INTEREST = frozenset({'Read', 'Edit', 'Write', 'NotebookEdit', 'MultiEdit'})

EXT_SKILLS = {
    '.go': '/go',
    '.rs': '/rs',
    '.py': '/py',
    '.ts': '/ts',
    '.tsx': '/tsx',
    '.sql': '/sql',
    '.sh': '/sh',
    '.bash': '/sh',
    '.zsh': '/sh',
    '.html': '/htmx',
    '.htm': '/htmx',
    '.jinja': '/htmx',
    '.j2': '/htmx',
    '.heex': '/htmx',
}


def skill_for(path: str) -> str | None:
    """Pure: map a file path to its language skill, or None."""
    if not isinstance(path, str) or not path:
        return None
    lower = os.path.basename(path).lower()
    if lower in ('makefile', 'gnumakefile') or lower.endswith(('.mk', '.make')):
        return '/mk'
    if lower == 'dockerfile' or lower.startswith('dockerfile.'):
        return '/ops'
    if lower in ('docker-compose.yml', 'docker-compose.yaml', 'compose.yml', 'compose.yaml'):
        return '/ops'
    if '.github/workflows/' in path or '/ansible/' in path:
        return '/ops'
    if lower.endswith(('.service', '.timer', '.socket', '.ansible.yml')):
        return '/ops'
    return EXT_SKILLS.get(os.path.splitext(lower)[1])


def extract_path(data: object) -> str:
    """Pure: pull file_path or notebook_path from a PreToolUse payload, '' if absent."""
    if not isinstance(data, dict):
        return ''
    ti = data.get('tool_input')
    if not isinstance(ti, dict):
        return ''
    return ti.get('file_path') or ti.get('notebook_path') or ''


def process(data: object) -> dict | None:
    """Pure: parsed hook JSON → hookSpecificOutput dict, or None for silent."""
    if not isinstance(data, dict) or data.get('tool_name') not in TOOLS_OF_INTEREST:
        return None
    path = extract_path(data)
    skill = skill_for(path)
    if not skill:
        return None
    return {
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'additionalContext': f'Editing/reading {os.path.basename(path)} — follow {skill} conventions.',
        },
    }


def already_seen(cache_file: str, key: str) -> bool:
    """Side-effecting: True if key is in cache. Silent on OSError."""
    try:
        with open(cache_file, encoding='utf-8', errors='replace') as fh:
            return key in {line.rstrip('\n') for line in fh}
    except OSError:
        return False


def remember(cache_file: str, key: str) -> None:
    """Side-effecting: append key to cache. Silent on OSError."""
    with contextlib.suppress(OSError), open(cache_file, 'a', encoding='utf-8') as fh:
        fh.write(key + '\n')


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        return
    result = process(data)
    if not result:
        return

    path = extract_path(data)
    skill = skill_for(path) or ''
    session = str(data.get('session_id') or 'default').replace('/', '_').replace('\\', '_')
    cache_dir = os.path.join(tempfile.gettempdir(), 'claude-extnudge')
    cache_file = os.path.join(cache_dir, f'{session}.txt')
    key = f'{skill}\t{path}'
    with contextlib.suppress(OSError):
        os.makedirs(cache_dir, exist_ok=True)
    if already_seen(cache_file, key):
        return
    remember(cache_file, key)
    with contextlib.suppress(OSError, ValueError):
        print(json.dumps(result))


# --- Tests ---------------------------------------------------------------
# Three layers: skill_for (path → skill mapping), extract_path (payload →
# path), process (wiring + tool filter). Pytest parametrization keeps the
# tables flat and adding a case = one tuple.

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
    ({}, ''),
    (None, ''),
    ('not-a-dict', ''),
]

PROCESS_CASES = [
    # (input, expected: True = emit nudge, False = silent)
    ({'tool_name': 'Read', 'tool_input': {'file_path': '/x.py'}}, True),
    ({'tool_name': 'Edit', 'tool_input': {'file_path': '/x.py'}}, True),
    ({'tool_name': 'Write', 'tool_input': {'file_path': '/x.py'}}, True),
    ({'tool_name': 'MultiEdit', 'tool_input': {'file_path': '/x.py'}}, True),
    ({'tool_name': 'NotebookEdit', 'tool_input': {'notebook_path': '/n.py'}}, True),
    ({'tool_name': 'Bash', 'tool_input': {'file_path': '/x.py'}}, False),
    ({'tool_name': 'Read'}, False),
    ({'tool_name': 'Read', 'tool_input': {'file_path': '/x.xyz'}}, False),
    ({'tool_name': None, 'tool_input': {'file_path': '/x.py'}}, False),
    ({}, False),
    ([], False),
    (None, False),
]

try:
    import pytest

    @pytest.mark.parametrize(
        ('path', 'skill'), SKILL_CASES, ids=[c[0] or '<empty>' for c in SKILL_CASES]
    )
    def test_skill_for(path, skill):
        assert skill_for(path) == skill

    @pytest.mark.parametrize(('payload', 'path'), PATH_CASES)
    def test_extract_path(payload, path):
        assert extract_path(payload) == path

    @pytest.mark.parametrize(('payload', 'should_emit'), PROCESS_CASES)
    def test_process(payload, should_emit):
        result = process(payload)
        assert (result is not None) == should_emit
        if should_emit:
            assert result['hookSpecificOutput']['hookEventName'] == 'PreToolUse'
            assert 'follow ' in result['hookSpecificOutput']['additionalContext']
except ImportError:
    pass


if __name__ == '__main__':
    # Hooks must never crash a tool call.
    with contextlib.suppress(Exception):
        main()
    sys.exit(0)
