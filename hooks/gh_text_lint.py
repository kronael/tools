#!/usr/bin/env python3
"""Lint text bound for GitHub: a PR body, an issue body or a review comment.

WISDOM § Git and the posting skill's Format section are the rules; this is
the part of them a program can check. pretool_nudge.py calls `command_reason`
to refuse a `gh` command whose body fails.

    python3 gh_text_lint.py pr tmp/pr-body.md --draft tmp/pr-draft.md --title '<title>'
    python3 gh_text_lint.py issue tmp/issue-body.md
    python3 gh_text_lint.py comment tmp/comment.md

Prints `<file>:<line>: <problem>` per failure and exits 1, else `ok: ...`.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from enum import Enum


class Kind(str, Enum):
    PR = 'pr'
    ISSUE = 'issue'
    COMMENT = 'comment'


@dataclass(frozen=True)
class Problem:
    """A lint failure; `line` is 0 when it is not bound to one line."""

    line: int
    text: str


ROBOT = '\U0001f916'
TLDR = '**TL;DR:**'
SKILL = {Kind.PR: 'pr-draft', Kind.ISSUE: 'gh-issue', Kind.COMMENT: 'gh-comment'}
MAX_CHARS = {Kind.PR: 3000, Kind.ISSUE: 3000, Kind.COMMENT: 240}
MAX_COMMENT_LINES = 2
MAX_FENCE_LINES = 6
MAX_TITLE = 72
SHOWN_PROBLEMS = 4
BANNED = (
    'generated with',
    'co-authored-by',
    'claude.com/claude-code',
    'claude.ai/',
    'noreply@anthropic.com',
)
MARKETING = re.compile(
    r'\b(?:robust|seamless|powerful|comprehensive|leverag(?:e|es|ed)|streamlin(?:e|es|ed)|excited)\b',
    re.IGNORECASE,
)
THIS_PR = re.compile(r'\bthis (?:pr|pull request)\b', re.IGNORECASE)
SHORTENED = re.compile(r'[0-9a-f]{4,}\.\.\.[0-9a-f]{2,}', re.IGNORECASE)
ELLIPSIS = '…'
HEADER = re.compile(r'^#{1,6}\s')
RULE = re.compile(r'^\s*(?:-{3,}|\*{3,}|_{3,})\s*$')
TABLE = re.compile(r'^\s*\|')
CHECKBOX = re.compile(r'^\s*[-*]\s+\[[ xX]\]')
FENCE = re.compile(r'^\s*(?:```|~~~)')

# A gh invocation at the head of a command segment, with its text kind and
# whether the command cannot do its job without a body.
GH = r'(?:^|[;&|\n]|\$\()\s*(?:timeout\s+\S+\s+)?gh\s+'
API = GH + r'api\b[^\n|;&]*'
POSTS = (
    (re.compile(GH + r'pr\s+create\b'), Kind.PR, True),
    (re.compile(GH + r'pr\s+edit\b'), Kind.PR, False),
    (re.compile(GH + r'issue\s+create\b'), Kind.ISSUE, True),
    (re.compile(GH + r'issue\s+edit\b'), Kind.ISSUE, False),
    (re.compile(GH + r'(?:pr|issue)\s+comment\b'), Kind.COMMENT, True),
    (re.compile(API + r'(?:/reviews|/comments|/replies)\b'), Kind.COMMENT, False),
    (re.compile(API + r'\bpulls/\d+(?![\w/])'), Kind.PR, False),
    (re.compile(API + r'\bissues/\d+(?![\w/])'), Kind.ISSUE, False),
)
HEREDOC = re.compile(r'<<-?\s*([\'"]?)(\w+)\1[^\n]*\n(.*?)\n[ \t]*\2[ \t]*(?:\n|$)', re.DOTALL)
JSON_BODY = re.compile(r'"body"\s*:\s*"((?:[^"\\]|\\.)*)"')
INPUT = re.compile(r'--input[ =](\S+)')
CAT_HEREDOC = re.compile(r'\$\(\s*cat\s*<<')
CAT_FILE = re.compile(r'\$\(\s*cat\s+([^)\s]+)\s*\)')
BODY_FILE = re.compile(r'(?:--body-file[ =]|(?<!\S)-F\s+(?!body=)|(?:-F|--field)\s+body=@)(\S+)')
BODY_TEXT = re.compile(
    r'(?:--body[ =]|(?<!\S)-b\s+|(?:-f|-F|--field|--raw-field)\s+body=)(["\'])(.*?)\1', re.DOTALL
)
TITLE = re.compile(r'(?:--title[ =]|(?<!\S)-t\s+)(["\'])(.*?)\1', re.DOTALL)


def split_prose(lines: list[str]) -> list[tuple[int, str]]:
    out, fenced = [], False
    for n, line in enumerate(lines, 1):
        if FENCE.match(line):
            fenced = not fenced
        elif not fenced:
            out.append((n, line))
    return out


def find_fences(lines: list[str]) -> list[tuple[int, int]]:
    out, start = [], 0
    for n, line in enumerate(lines, 1):
        if not FENCE.match(line):
            continue
        if start:
            out.append((start, n - start - 1))
            start = 0
        else:
            start = n
    return out


def lint_common(kind: Kind, lines: list[str], body: str) -> list[Problem]:
    problems = []
    for n, line in enumerate(lines, 1):
        lower = line.lower()
        problems += [
            Problem(n, f'banned attribution "{b}": the only attribution is a bare {ROBOT}')
            for b in BANNED
            if b in lower
        ]
        if ELLIPSIS in line or SHORTENED.search(line):
            problems.append(Problem(n, 'shortened address, hash or sentence: write it in full'))
        problems += [Problem(n, f'marketing word "{m.group()}"') for m in MARKETING.finditer(line)]
        if THIS_PR.search(line):
            problems.append(Problem(n, '"this PR": name what the change does instead'))
    if len(body) > MAX_CHARS[kind]:
        problems.append(Problem(0, f'{len(body)} chars, cap {MAX_CHARS[kind]}: cut, or link a doc'))
    return problems


def lint_signed(lines: list[str]) -> list[Problem]:
    problems = [
        Problem(n, 'checkbox: no test plan or checklist')
        for n, line in enumerate(lines, 1)
        if CHECKBOX.match(line)
    ]
    if lines[-1].strip() != ROBOT:
        problems.append(Problem(len(lines), f'last line must be a bare {ROBOT} and nothing else'))
    problems += [
        Problem(n, f'{ROBOT} belongs on the last line only')
        for n, line in enumerate(lines[:-1], 1)
        if ROBOT in line
    ]
    return problems


def lint_pr(lines: list[str]) -> list[Problem]:
    problems = []
    first = next((line for line in lines if line.strip()), '')
    if not first.startswith(TLDR):
        problems.append(Problem(1, f'open with {TLDR} and the outcome, not a header or narrative'))
    for n, line in split_prose(lines):
        if HEADER.match(line):
            problems.append(
                Problem(n, 'header: one paragraph per concern, opened by a bold lead-in')
            )
        if RULE.match(line):
            problems.append(Problem(n, 'horizontal rule'))
        if TABLE.match(line):
            problems.append(Problem(n, 'table: fold it into prose or link a doc'))
    problems += [
        Problem(n, f'{k}-line code block restates the diff: point at the file instead')
        for n, k in find_fences(lines)
        if k > MAX_FENCE_LINES
    ]
    return problems


def lint_comment(lines: list[str]) -> list[Problem]:
    problems = []
    if not lines[0].startswith(ROBOT + ' '):
        problems.append(Problem(1, f'comment must start with "{ROBOT} "'))
    full = [n for n, line in enumerate(lines, 1) if line.strip()]
    if len(full) > MAX_COMMENT_LINES:
        problems.append(
            Problem(
                full[MAX_COMMENT_LINES],
                f'{len(full)} lines, cap {MAX_COMMENT_LINES}: split the finding'
                ' or keep the evidence for the report',
            )
        )
    return problems


def lint_title(title: str) -> list[Problem]:
    problems = []
    if len(title) > MAX_TITLE:
        problems.append(Problem(0, f'title {len(title)} chars, max {MAX_TITLE}'))
    if title.count(' and ') >= 2:
        problems.append(Problem(0, 'title lists changes: name the one outcome above them'))
    return problems


def lint(
    kind: Kind, text: str, title: str | None = None, draft: str | None = None
) -> list[Problem]:
    body = text.rstrip()
    if not body:
        return [Problem(0, 'empty body')]
    lines = body.split('\n')
    problems = lint_common(kind, lines, body)
    problems += lint_comment(lines) if kind is Kind.COMMENT else lint_signed(lines)
    if kind is Kind.PR:
        problems += lint_pr(lines)
        if draft is not None and len(body) >= len(draft.rstrip()):
            problems.append(
                Problem(
                    0, f'DISTILL cut nothing: body {len(body)} chars, draft {len(draft.rstrip())}'
                )
            )
    if title is not None:
        problems += lint_title(title)
    return problems


def read_file(path: str, cwd: str) -> str:
    """The file's text, or the reason it cannot be the body a hook checks."""
    path = path.strip('"\'')
    if re.search(r'[$`]', path):
        raise OSError(f'cannot read the body from {path}: pass a literal path')
    try:
        with open(os.path.join(cwd, path), encoding='utf-8') as fh:
            return fh.read()
    except OSError as err:
        raise OSError(f'cannot read the body file {path}: {err.strerror}') from err


def json_bodies(text: str) -> list[str]:
    return [json.loads(f'"{m}"') for m in JSON_BODY.findall(text) if m]


def read_bodies(command: str, cwd: str) -> list[str]:
    """Every body text the command posts; OSError names a body it cannot read."""
    doc = HEREDOC.search(command)
    heredoc = doc.group(3) if doc else ''
    given = INPUT.search(command)
    if given:
        text = heredoc if given.group(1) == '-' else read_file(given.group(1), cwd)
        return json_bodies(text)
    if CAT_HEREDOC.search(command):
        return [heredoc]
    cat = CAT_FILE.search(command)
    if cat:
        return [read_file(cat.group(1), cwd)]
    named = BODY_FILE.search(command)
    if named:
        return [heredoc if named.group(1) == '-' else read_file(named.group(1), cwd)]
    inline = BODY_TEXT.search(command)
    if not inline:
        return []
    if re.search(r'\$\(|`', inline.group(2)):
        raise OSError('the body is built by a command substitution: pass a literal path')
    return [inline.group(2)]


def describe(problems: list[Problem]) -> str:
    shown = '; '.join(
        f'L{p.line} {p.text}' if p.line else p.text for p in problems[:SHOWN_PROBLEMS]
    )
    more = len(problems) - SHOWN_PROBLEMS
    return shown + (f' (+{more} more)' if more > 0 else '')


def command_reason(command: str, cwd: str | None = None) -> str | None:
    """Why a gh command that posts text must not run, or None when it may."""
    post = next(
        ((kind, required) for pattern, kind, required in POSTS if pattern.search(command)), None
    )
    if post is None:
        return None
    kind, required = post
    try:
        bodies = read_bodies(command, cwd or os.getcwd())
    except OSError as err:
        return str(err)
    if not bodies:
        if not required:
            return None
        return (
            f'{kind.value} body not found in the command: write it with the {SKILL[kind]} skill,'
            f' lint it, and pass --body-file <path>'
        )
    title = TITLE.search(command)
    for body in bodies:
        problems = lint(kind, body, title.group(2) if title and kind is Kind.PR else None)
        if problems:
            return (
                f'GitHub {kind.value} text refused: {describe(problems)}. Fix it per the'
                f' {SKILL[kind]} skill: python3 ~/.claude/hooks/gh_text_lint.py {kind.value} <file>'
            )
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description='Lint text bound for GitHub')
    parser.add_argument('kind', choices=[k.value for k in Kind])
    parser.add_argument('file')
    parser.add_argument('--draft', help='the uncut first version; the body must be shorter')
    parser.add_argument('--title', help='the PR title to check beside the body')
    args = parser.parse_args()
    with open(args.file, encoding='utf-8') as fh:
        text = fh.read()
    draft = None
    if args.draft:
        with open(args.draft, encoding='utf-8') as fh:
            draft = fh.read()
    problems = lint(Kind(args.kind), text, args.title, draft)
    for p in problems:
        where = f'{args.file}:{p.line}' if p.line else args.file
        print(f'{where}: {p.text}')
    if problems:
        print(f'fail: {len(problems)} problem(s)')
        return 1
    n = len(text.rstrip())
    cut = f', draft {len(draft.rstrip())} -> {100 * n // len(draft.rstrip())}%' if draft else ''
    print(f'ok: {args.kind} {n} chars{cut}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
