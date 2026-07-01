#!/usr/bin/env python3
# PreToolUse hook: emit a per-language skill nudge based on file extension.
# Production: silent-fail on any error (NEVER block a tool call). Tests:
# `pytest hooks/pretool_nudge.py` or `make test`.
import contextlib
import json
import os
import sys

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
    cache_dir = os.path.expanduser('~/.claude/tmp/extnudge')
    cache_file = os.path.join(cache_dir, f'{session}.txt')
    key = f'{skill}\t{path}'
    with contextlib.suppress(OSError):
        os.makedirs(cache_dir, exist_ok=True)
    if already_seen(cache_file, key):
        return
    remember(cache_file, key)
    with contextlib.suppress(OSError, ValueError):
        print(json.dumps(result))


if __name__ == '__main__':
    # Hooks must never crash a tool call.
    with contextlib.suppress(Exception):
        main()
    sys.exit(0)
