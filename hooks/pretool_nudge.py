#!/usr/bin/env python3
# PreToolUse hook: emit a per-language skill nudge based on file extension.
#
# Production: silent-fail on any error (NEVER block a tool call with a
# Traceback). Tests: `pytest hooks/pretool_nudge.py` runs the bundled
# parametrized cases against the pure `process()` function.
import contextlib
import json
import os
import sys
import tempfile

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
    basename = os.path.basename(path)
    lower = basename.lower()
    if lower in ('makefile', 'gnumakefile') or lower.endswith(('.mk', '.make')):
        return '/mk'
    if lower == 'dockerfile' or lower.startswith('dockerfile.'):
        return '/ops'
    if lower in ('docker-compose.yml', 'docker-compose.yaml', 'compose.yml', 'compose.yaml'):
        return '/ops'
    if '/.github/workflows/' in path or path.startswith('.github/workflows/'):
        return '/ops'
    if '/ansible/' in path or lower.endswith('.ansible.yml'):
        return '/ops'
    if lower.endswith(('.service', '.timer', '.socket')):
        return '/ops'
    _, ext = os.path.splitext(lower)
    return EXT_SKILLS.get(ext)


def process(data: dict) -> dict | None:
    """Pure: take parsed hook JSON, return the hookSpecificOutput dict or None."""
    if not isinstance(data, dict):
        return None
    if data.get('tool_name') not in ('Read', 'Edit', 'Write', 'NotebookEdit', 'MultiEdit'):
        return None
    ti = data.get('tool_input') or {}
    if not isinstance(ti, dict):
        return None
    path = ti.get('file_path') or ti.get('notebook_path') or ''
    skill = skill_for(path)
    if not skill:
        return None
    basename = os.path.basename(path) if isinstance(path, str) else ''
    return {
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'additionalContext': f'Editing/reading {basename} — follow {skill} conventions.',
        },
    }


def already_seen(cache_file: str, key: str) -> bool:
    """Side-effecting: check if key is in cache. Silent on OSError."""
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

    # De-dup nudge for the same skill+path within a session.
    session = str(data.get('session_id') or 'default').replace('/', '_').replace('\\', '_')
    cache_dir = os.path.join(tempfile.gettempdir(), 'claude-extnudge')
    cache_file = os.path.join(cache_dir, f'{session}.txt')
    skill = result['hookSpecificOutput']['additionalContext'].split('follow ')[1].split(' ')[0]
    path = (
        (data.get('tool_input') or {}).get('file_path')
        or (data.get('tool_input') or {}).get('notebook_path')
        or ''
    )
    key = f'{skill}\t{path}'
    with contextlib.suppress(OSError):
        os.makedirs(cache_dir, exist_ok=True)
    if already_seen(cache_file, key):
        return
    remember(cache_file, key)

    with contextlib.suppress(OSError, ValueError):
        print(json.dumps(result))


# --- Self-tests ----------------------------------------------------------

TEST_CASES = [
    # (name, input dict, predicate on process() result)
    (
        'tsx → /tsx',
        {'tool_name': 'Read', 'tool_input': {'file_path': '/proj/foo.tsx'}},
        lambda r: r and '/tsx' in r['hookSpecificOutput']['additionalContext'],
    ),
    (
        'py → /py',
        {'tool_name': 'Read', 'tool_input': {'file_path': '/proj/foo.py'}},
        lambda r: r and '/py' in r['hookSpecificOutput']['additionalContext'],
    ),
    (
        'Makefile → /mk',
        {'tool_name': 'Edit', 'tool_input': {'file_path': '/p/Makefile'}},
        lambda r: r and '/mk' in r['hookSpecificOutput']['additionalContext'],
    ),
    (
        'Dockerfile → /ops',
        {'tool_name': 'Read', 'tool_input': {'file_path': '/p/Dockerfile'}},
        lambda r: r and '/ops' in r['hookSpecificOutput']['additionalContext'],
    ),
    (
        '.github/workflows → /ops',
        {'tool_name': 'Edit', 'tool_input': {'file_path': '/repo/.github/workflows/ci.yml'}},
        lambda r: r and '/ops' in r['hookSpecificOutput']['additionalContext'],
    ),
    (
        'htmx alias',
        {'tool_name': 'Edit', 'tool_input': {'file_path': '/t/page.html'}},
        lambda r: r and '/htmx' in r['hookSpecificOutput']['additionalContext'],
    ),
    (
        'unknown ext → silent',
        {'tool_name': 'Read', 'tool_input': {'file_path': '/proj/foo.xyz'}},
        lambda r: r is None,
    ),
    (
        'non-routed tool → silent',
        {'tool_name': 'Bash', 'tool_input': {'file_path': '/proj/foo.py'}},
        lambda r: r is None,
    ),
    ('null tool_input → silent', {'tool_name': 'Read', 'tool_input': None}, lambda r: r is None),
    (
        'null file_path → silent',
        {'tool_name': 'Read', 'tool_input': {'file_path': None}},
        lambda r: r is None,
    ),
    (
        'non-string file_path → silent',
        {'tool_name': 'Read', 'tool_input': {'file_path': 123}},
        lambda r: r is None,
    ),
    ('empty dict → silent', {}, lambda r: r is None),
    ('non-dict input → silent', [], lambda r: r is None),
]


# Pytest discovery: `pytest hooks/pretool_nudge.py` runs each TEST_CASES tuple
# as a parametrized test against `process()`. pytest is an optional dev dep —
# the conditional import keeps production hook runs free of it.
try:
    import pytest

    @pytest.mark.parametrize(
        ('name', 'inp', 'check'),
        TEST_CASES,
        ids=[c[0] for c in TEST_CASES],
    )
    def test_process(name, inp, check):
        result = process(inp)
        assert check(result), f'{name}: got {result!r}'
except ImportError:
    pass


if __name__ == '__main__':
    # Hooks must never crash a tool call. Swallow every exception silently —
    # diagnostics belong in `pytest` runs, not in user-facing tool dispatch.
    with contextlib.suppress(Exception):
        main()
    sys.exit(0)
