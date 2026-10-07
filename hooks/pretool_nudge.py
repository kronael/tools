#!/usr/bin/env python3
# PreToolUse hook: block unsafe commands and emit per-language file nudges.
# Production: silent-fail on any error except explicit unsafe-command blocks.
from __future__ import annotations

import contextlib
import json
import os
import re
import sys

TOOLS_OF_INTEREST = frozenset({'Read', 'Edit', 'Write', 'NotebookEdit', 'MultiEdit', 'apply_patch'})
COMMAND_TOOLS = frozenset({'Bash', 'exec_command'})
UNSAFE_COMMAND_PATTERNS = (
    (r'(?<!\S)git\s+reset\s+--hard\b', 'git reset --hard'),
    (r'(?<!\S)git\s+add\s+(?:-A|--all)\b', 'broad git add'),
    (r'(?<!\S)git\s+commit\b[^\n;|&]*\s--amend\b', 'git commit --amend'),
    (r'(?<!\S)git\s+commit\b[^\n;|&]*\s--no-verify\b', 'git commit --no-verify'),
    (r'(?<!\S)git\s+commit\b[\s\S]*(?i:co-authored-by)', 'Co-Authored-By trailer'),
    (r'(?<!\S)git\s+merge\b[^\n;|&]*\s--squash\b', 'git merge --squash'),
    (r'(?<!\S)git\s+rebase\b[^\n;|&]*\s(?:-i|--interactive)\b', 'git rebase -i'),
    (r'(?<!\S)git\s+(?:checkout|switch)\b[^\n;|&]*\s-[bBcC]\b', 'git branch creation'),
    (r'(?<!\S)git\s+worktree\s+add\b(?![^\n;|&]*--detach)', 'git worktree add without --detach'),
    (r'(?<!\S)killall\b', 'killall'),
    (r'(?<!\S)rm\s+-[^\s;|&]*r[^\s;|&]*f\b', 'rm -rf'),
    (r'(?<!\S)rm\s+-[^\s;|&]*f[^\s;|&]*r\b', 'rm -rf'),
    # Any recursive removal, not only -rf: -r, -R and --recursive delete
    # trees just as thoroughly, and the deny rules ban all three.
    (r'(?<!\S)rm\s+(?:-[a-zA-Z]*[rR]|--recursive)', 'recursive rm'),
)

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
CODE_SKILLS = frozenset({*EXT_SKILLS.values(), '/mk'})


def skill_for(path: str) -> str | None:
    """Pure: map a file path to its language skill, or None."""
    if not isinstance(path, str) or not path:
        return None
    lower = os.path.basename(path).lower()
    if lower == 'skill.md' or lower in ('claude.md', 'agents.md'):
        return '/wisdom'
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
    if data.get('tool_name') == 'apply_patch':
        path = extract_apply_patch_path(ti)
        if path:
            return path
    return ti.get('file_path') or ti.get('notebook_path') or ''


def extract_apply_patch_path(tool_input: dict) -> str:
    patch = tool_input.get('patch')
    if not isinstance(patch, str):
        return ''
    prefixes = (
        '*** Add File: ',
        '*** Update File: ',
        '*** Delete File: ',
    )
    for line in patch.splitlines():
        for prefix in prefixes:
            if line.startswith(prefix):
                return line[len(prefix) :].strip()
    return ''


def extract_command(data: object) -> str:
    if not isinstance(data, dict):
        return ''
    ti = data.get('tool_input')
    if not isinstance(ti, dict):
        return ''
    value = ti.get('command') or ti.get('cmd')
    if isinstance(value, str):
        return value
    return ''


def unsafe_command_reason(command: str, harness: str | None = None) -> str | None:
    for pattern, reason in UNSAFE_COMMAND_PATTERNS:
        if re.search(pattern, command):
            return reason
    if harness == 'codex' and re.search(r'(?<!\S)codex\b', command):
        return 'recursive codex execution'
    return None


def process(data: object) -> dict | None:
    """Pure: parsed hook JSON → hookSpecificOutput dict, or None for silent."""
    if isinstance(data, dict) and data.get('tool_name') in COMMAND_TOOLS:
        command = extract_command(data)
        reason = unsafe_command_reason(command, data.get('harness'))
        if reason:
            return {
                'decision': 'block',
                'reason': f'block: unsafe command blocked ({reason}).',
            }
        return None

    if not isinstance(data, dict) or data.get('tool_name') not in TOOLS_OF_INTEREST:
        return None
    path = extract_path(data)
    skill = skill_for(path)
    if not skill:
        return None
    code = ' Read ~/.claude/skills/software/code.md first.' if skill in CODE_SKILLS else ''
    return {
        'hookSpecificOutput': {
            'hookEventName': 'PreToolUse',
            'additionalContext': f'Editing/reading {os.path.basename(path)} — follow {skill} conventions.{code}',
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

    # A block is a ban and must fire on EVERY unsafe command. The dedup cache
    # below keys on (skill, path); a Bash call carries neither, so all of them
    # share one key and the second unsafe command in a session goes through.
    if result.get('decision') == 'block':
        with contextlib.suppress(OSError, ValueError):
            print(json.dumps(result))
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
