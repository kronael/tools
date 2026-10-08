#!/usr/bin/env python3
# PostToolUse hook: run rumdl on the Markdown files a write tool touched.
# Silent unless the file's own repository holds a rumdl config, so only a repo
# that opted in is rewrapped. Advisory only; the tool already ran.
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

from pretool_nudge import apply_patch_paths
from pretool_nudge import extract_path

# The fallback when neither the repo nor PATH has rumdl; a repo's own pin wins.
RUMDL_VERSION = '0.2.78'
WRITE_TOOLS = frozenset({'Write', 'Edit', 'MultiEdit', 'apply_patch'})
CONFIG_NAMES = ('.rumdl.toml', 'rumdl.toml')
PYPROJECT_SECTION = re.compile(r'^\s*\[tool\.rumdl(?:\]|\.)', re.MULTILINE)
TIMEOUT_S = 20
# `rumdl fmt` exits 0 whether or not an issue remains; a leftover is a finding
# line it did not mark fixed. The line shape holds only for the text format,
# which an environment or config setting can switch to JSON.
FINDING = re.compile(r':\d+:\d+: \[MD\d+\] ')
TEXT_OUTPUT = {'RUMDL_OUTPUT_FORMAT': 'text'}


def markdown_paths(data: object) -> list[str]:
    """Pure: the Markdown files a write tool touched, in tool order."""
    if not isinstance(data, dict) or data.get('tool_name') not in WRITE_TOOLS:
        return []
    tool_input = data.get('tool_input')
    if data.get('tool_name') == 'apply_patch' and isinstance(tool_input, dict):
        paths = apply_patch_paths(tool_input)
    else:
        paths = [extract_path(data)]
    return [path for path in paths if path.lower().endswith(('.md', '.markdown'))]


def ancestors(directory: str) -> Iterator[str]:
    """Pure: the directory and its parents, ending at the repository root (the
    first one holding `.git`), so a nested foreign clone never inherits a
    config or a binary from the tree above it."""
    current = os.path.abspath(directory)
    while True:
        yield current
        parent = os.path.dirname(current)
        if parent == current or os.path.exists(os.path.join(current, '.git')):
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
            if PYPROJECT_SECTION.search(fh.read()):
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
    changed, nothing is left and rumdl exited 0."""
    directory, name = os.path.split(os.path.abspath(path))
    before = read_bytes(path)
    notes = []
    try:
        result = run(
            [*command, '--color', 'never', 'fmt', '--', name],
            cwd=directory,
            env={**os.environ, **TEXT_OUTPUT},
            capture_output=True,
            encoding='utf-8',
            errors='replace',
            timeout=TIMEOUT_S,
        )
    except (OSError, subprocess.SubprocessError) as err:
        result = None
        notes.append(f'rumdl failed on {name}: {err}')
    if read_bytes(path) != before:
        notes.insert(0, f'rumdl reformatted {name}; Read it again before the next Edit.')
    if result is not None:
        output = f'{result.stdout}{result.stderr}'
        remaining = leftovers(output)
        if remaining:
            notes.append('rumdl could not fix: ' + ' | '.join(remaining[:5]))
        if result.returncode != 0:
            last = next(
                (line.strip() for line in reversed(output.splitlines()) if line.strip()), ''
            )
            notes.append(f'rumdl exited {result.returncode} on {name}: {last}')
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
    find_config_fn: Callable[[str], str | None] = find_config,
    find_rumdl_fn: Callable[[str], list[str] | None] = find_rumdl,
    format_fn: Callable[[str, list[str]], str | None] = format_file,
    is_file_fn: Callable[[str], bool] = os.path.isfile,
) -> dict | None:
    """Parsed hook JSON → hookSpecificOutput dict, or None for silent. A path
    the tool deleted or moved away is skipped."""
    notes = []
    for path in markdown_paths(data):
        if not is_file_fn(path):
            continue
        directory = os.path.dirname(os.path.abspath(path))
        if find_config_fn(directory) is None:
            continue
        command = find_rumdl_fn(directory)
        if command is None:
            notes.append(
                f'{os.path.basename(path)} is under a rumdl config but no rumdl is installed:'
                " install the repo's pin (`make prepare`) or `uv tool install rumdl`."
            )
            continue
        note = format_fn(path, command)
        if note:
            notes.append(note)
    return context(' '.join(notes)) if notes else None


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
    try:
        main()
    except Exception as err:
        print(f'md_format: {err}', file=sys.stderr)
    sys.exit(0)
