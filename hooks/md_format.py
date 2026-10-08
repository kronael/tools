#!/usr/bin/env python3
# PostToolUse hook: run rumdl on the Markdown file a write tool touched.
# Silent unless an ancestor directory holds a rumdl config, so only a repo that
# opted in is rewrapped. Advisory only; the tool already ran.
from __future__ import annotations

import contextlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Callable
from collections.abc import Iterator

from pretool_nudge import extract_path

# The fallback when neither the repo nor PATH has rumdl; a repo's own pin wins.
RUMDL_VERSION = '0.2.78'
WRITE_TOOLS = frozenset({'Write', 'Edit', 'MultiEdit', 'apply_patch'})
CONFIG_NAMES = ('.rumdl.toml', 'rumdl.toml')
TIMEOUT_S = 20
# `rumdl fmt` exits 0 whether or not an issue remains; a leftover is a finding
# line it did not mark fixed.
FINDING = re.compile(r':\d+:\d+: \[MD\d+\] ')


def markdown_path(data: object) -> str | None:
    """Pure: the Markdown file a write tool touched, or None."""
    if not isinstance(data, dict) or data.get('tool_name') not in WRITE_TOOLS:
        return None
    path = extract_path(data)
    if not path.lower().endswith(('.md', '.markdown')):
        return None
    return path


def ancestors(directory: str) -> Iterator[str]:
    current = os.path.abspath(directory)
    while True:
        yield current
        parent = os.path.dirname(current)
        if parent == current:
            return
        current = parent


def find_config(directory: str) -> str | None:
    """Side-effecting: the nearest rumdl config above the file, or None."""
    for folder in ancestors(directory):
        for name in CONFIG_NAMES:
            candidate = os.path.join(folder, name)
            if os.path.isfile(candidate):
                return candidate
        pyproject = os.path.join(folder, 'pyproject.toml')
        with (
            contextlib.suppress(OSError),
            open(pyproject, encoding='utf-8', errors='replace') as fh,
        ):
            if '[tool.rumdl]' in fh.read():
                return pyproject
    return None


def find_rumdl(
    directory: str, which: Callable[[str], str | None] = shutil.which
) -> list[str] | None:
    """Side-effecting: the repo's pinned binary, else PATH, else a pinned uvx run."""
    for folder in ancestors(directory):
        candidate = os.path.join(folder, 'node_modules', '.bin', 'rumdl')
        if os.access(candidate, os.X_OK):
            return [candidate]
    found = which('rumdl')
    if found:
        return [found]
    if which('uvx'):
        return ['uvx', f'rumdl@{RUMDL_VERSION}']
    return None


def leftovers(output: str) -> list[str]:
    """Pure: the findings rumdl reported and did not fix."""
    return [
        line.strip()
        for line in output.splitlines()
        if FINDING.search(line) and not line.rstrip().endswith('[fixed]')
    ]


def read_bytes(path: str) -> bytes | None:
    try:
        with open(path, 'rb') as fh:
            return fh.read()
    except OSError:
        return None


def format_file(
    path: str,
    command: list[str],
    run: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> str | None:
    """Side-effecting: `rumdl fmt` on the file from its own directory, so the
    nearest config applies. Returns the note for Claude, or None when nothing
    changed and nothing is left."""
    directory, name = os.path.split(os.path.abspath(path))
    before = read_bytes(path)
    try:
        result = run(
            [*command, 'fmt', name],
            cwd=directory,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_S,
        )
    except (OSError, subprocess.SubprocessError) as err:
        return f'rumdl failed on {name}: {err}'
    output = f'{result.stdout}{result.stderr}'
    notes = []
    if read_bytes(path) != before:
        notes.append(f'rumdl reformatted {name}; Read it again before the next Edit.')
    remaining = leftovers(output)
    if remaining:
        notes.append('rumdl could not fix: ' + ' | '.join(remaining[:5]))
    return ' '.join(notes) or None


def context(note: str) -> dict:
    return {
        'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': note,
        },
    }


def process(
    data: object,
    config: Callable[[str], str | None] = find_config,
    rumdl: Callable[[str], list[str] | None] = find_rumdl,
    fmt: Callable[[str, list[str]], str | None] = format_file,
) -> dict | None:
    """Parsed hook JSON → hookSpecificOutput dict, or None for silent."""
    path = markdown_path(data)
    if path is None:
        return None
    directory = os.path.dirname(os.path.abspath(path))
    if config(directory) is None:
        return None
    command = rumdl(directory)
    if command is None:
        return context(
            f'{os.path.basename(path)} is under a rumdl config but no rumdl is installed:'
            " install the repo's pin (`make prepare`) or `uv tool install rumdl`."
        )
    note = fmt(path, command)
    return context(note) if note else None


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        return
    result = process(data)
    if result:
        with contextlib.suppress(OSError, ValueError):
            print(json.dumps(result))


if __name__ == '__main__':
    # Hooks must never crash a tool call.
    with contextlib.suppress(Exception):
        main()
    sys.exit(0)
