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
MAX_FENCE_LINES = 6
MAX_TITLE = 72
SHOWN_PROBLEMS = 4
BANNED = (
    'generated with claude',
    'generated with [claude',
    'co-authored-by',
    'claude.com/claude-code',
    'claude.ai/',
    'noreply@anthropic.com',
)
MARKETING = re.compile(
    r'\b(?:robust|seamless|powerful|comprehensive|leverag\w*|streamlin\w*|excited)\b',
    re.IGNORECASE,
)
THIS_PR = re.compile(r'\bthis (?:pr|pull request)\b', re.IGNORECASE)
SHORTENED = re.compile(r'\w{4,}\.\.\.\w{2,}')
ELLIPSIS = '…'
HEADER = re.compile(r'^#{1,6}\s')
RULE = re.compile(r'^\s*(?:-{3,}|\*{3,}|_{3,})\s*$')
TABLE = re.compile(r'^\s*\|')
CHECKBOX = re.compile(r'^\s*[-*]\s+\[[ xX]\]')
FENCE = re.compile(r'^\s*(?:```|~~~)')

# A gh invocation at the head of a command segment, after any VAR=value
# assignments and one wrapper (env, timeout, sudo ...) with its arguments.
PREFIX = r'(?:\w+=\S*\s+)*(?:(?:env|command|exec|timeout|sudo|nice|nohup)\s+(?:\S+\s+)*?)?(?:\S*/)?'
GH = r'(?:^|[;&|(\n!]|\$\(|\b(?:if|then|else|elif|do|while|until)\s)\s*' + PREFIX + r'(?P<gh>gh\s+'
API = GH + r'api\b[^\n|;&]*'
POSTS = (
    (re.compile(GH + r'pr\s+create\b)'), Kind.PR, True),
    (re.compile(GH + r'pr\s+edit\b)'), Kind.PR, False),
    (re.compile(GH + r'issue\s+create\b)'), Kind.ISSUE, True),
    (re.compile(GH + r'issue\s+edit\b)'), Kind.ISSUE, False),
    (re.compile(GH + r'(?:pr|issue)\s+comment\b)'), Kind.COMMENT, True),
    (re.compile(GH + r'pr\s+review\b)'), Kind.COMMENT, False),
    (re.compile(API + r'(?:/reviews|/comments|/replies)\b)'), Kind.COMMENT, False),
    (re.compile(API + r'\bpulls/\d+(?![\w/]))'), Kind.PR, False),
    (re.compile(API + r'\bissues/\d+(?![\w/]))'), Kind.ISSUE, False),
)
HEREDOC = re.compile(r'<<-?\s*([\'"]?)(\w+)\1[^\n]*\n(.*?)\n[ \t]*\2[ \t]*(?:\n|$)', re.DOTALL)
MARK = '\x00'
MARKED = re.compile(f'{MARK}(\\d+){MARK}')
CD = re.compile(r'(?:^|[;&|(\n]|\b(?:then|do)\s)\s*cd\s+([^\s;&|)]+)')
QUOTED = r'(?:"((?:[^"\\]|\\.)*)"|\'([^\']*)\'|([^\s;&|)]+))'
INPUT = re.compile(r'--input[ =]' + QUOTED)
BODY_FILE = re.compile(
    r'(?:--body-file[ =]|(?:-F|--field)\s+body=@|(?<!\S)-F\s+(?![\w-]+=))' + QUOTED
)
BODY_TEXT = re.compile(
    r'(?:--body[ =]|(?<!\S)-b\s+|(?:-f|-F|--field|--raw-field)\s+body=)' + QUOTED
)
TITLE = re.compile(r'(?:--title[ =]|(?<!\S)-t\s+)' + QUOTED)
CAT_FILE = re.compile(r'^\$\(\s*cat\s+' + QUOTED + r'\s*\)$')
CAT_HEREDOC = re.compile(r'^\$\(\s*cat\s*<<')
JSON_BODY = re.compile(r'"body"\s*:\s*"((?:[^"\\]|\\.)*)"')


def split_prose(lines: list[str]) -> list[tuple[int, str]]:
    out = []
    fenced = False
    for n, line in enumerate(lines, 1):
        if FENCE.match(line):
            fenced = not fenced
        elif not fenced:
            out.append((n, line))
    return out


def find_fences(lines: list[str]) -> list[tuple[int, int]]:
    out = []
    start = 0
    for n, line in enumerate(lines, 1):
        if not FENCE.match(line):
            continue
        if start:
            out.append((start, n - start - 1))
            start = 0
        else:
            start = n
    if start:
        out.append((start, len(lines) - start))
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
    if len(body) > MAX_CHARS[kind]:
        problems.append(Problem(0, f'{len(body)} chars, cap {MAX_CHARS[kind]}: cut, or link a doc'))
    return problems


def lint_last_line(lines: list[str]) -> list[Problem]:
    if lines[-1].strip() == ROBOT:
        return []
    return [Problem(len(lines), f'last line must be a bare {ROBOT} and nothing else')]


def lint_pr(lines: list[str]) -> list[Problem]:
    problems = []
    first = next((line for line in lines if line.strip()), '')
    if not first.startswith(TLDR):
        problems.append(Problem(1, f'open with {TLDR} and the outcome, not a header or narrative'))
    for n, line in enumerate(lines, 1):
        if CHECKBOX.match(line):
            problems.append(Problem(n, 'checkbox: no test plan or checklist'))
        if THIS_PR.search(line):
            problems.append(Problem(n, '"this PR": name what the change does instead'))
        if ROBOT in line and n < len(lines):
            problems.append(Problem(n, f'{ROBOT} belongs on the last line only'))
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
    first = next((line for line in lines if line.strip()), '')
    if first.startswith(ROBOT + ' '):
        return []
    return [Problem(1, f'comment must start with "{ROBOT} "')]


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
    problems += lint_comment(lines) if kind is Kind.COMMENT else lint_last_line(lines)
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


def mark_heredocs(command: str) -> tuple[str, list[str]]:
    """The command with each heredoc's content replaced by a marker, and the contents."""
    docs = []

    def swap(m: re.Match) -> str:
        docs.append(m.group(3))
        head = m.group(0)[: m.start(3) - m.start()]
        tail = m.group(0)[m.end(3) - m.start() :]
        return f'{head}{MARK}{len(docs) - 1}{MARK}{tail}'

    return HEREDOC.sub(swap, command), docs


def quoted(m: re.Match) -> str:
    """The value a QUOTED match captured, with double-quote escapes removed."""
    if m.group(1) is not None:
        return re.sub(r'\\(["\\$`])', r'\1', m.group(1))
    return m.group(2) if m.group(2) is not None else m.group(3)


def read_file(path: str, cwd: str) -> str:
    """The file's text, or an OSError saying why it cannot be the body a hook checks."""
    if re.search(r'[$`]', path):
        raise OSError(f'cannot read the body from {path}: pass a literal path')
    try:
        with open(os.path.join(cwd, path), encoding='utf-8') as fh:
            return fh.read()
    except FileNotFoundError as err:
        raise OSError(
            f'cannot read the body file {path}: {err.strerror}; write it in its own call first'
        ) from err
    except (OSError, UnicodeDecodeError) as err:
        raise OSError(f'cannot read the body file {path}: {err}') from err


def json_bodies(text: str) -> list[str]:
    try:
        return [json.loads(f'"{m}"') for m in JSON_BODY.findall(text) if m]
    except json.JSONDecodeError as err:
        raise OSError(f'cannot parse the JSON body: {err}') from err


def heredoc_in(segment: str, docs: list[str]) -> str | None:
    m = MARKED.search(segment)
    return docs[int(m.group(1))] if m else None


def read_bodies(segment: str, docs: list[str], cwd: str) -> list[str]:
    """Every body text the segment posts; OSError names a body it cannot read."""
    doc = heredoc_in(segment, docs)
    given = INPUT.search(segment)
    if given:
        path = quoted(given)
        if path != '-':
            return json_bodies(read_file(path, cwd))
        if doc is None:
            raise OSError('--input - reads stdin the hook cannot see: pass a file or a heredoc')
        return json_bodies(doc)
    named = BODY_FILE.search(segment)
    if named:
        path = quoted(named)
        if path != '-':
            return [read_file(path, cwd)]
        if doc is None:
            raise OSError('--body-file - reads stdin the hook cannot see: pass a file or a heredoc')
        return [doc]
    inline = BODY_TEXT.search(segment)
    if not inline:
        return []
    text = quoted(inline)
    if CAT_HEREDOC.match(text):
        if doc is None:
            raise OSError('the body heredoc was not found: pass a file or a complete heredoc')
        return [doc]
    cat = CAT_FILE.match(text)
    if cat:
        return [read_file(quoted(cat), cwd)]
    if '$(' in text or (inline.lastindex == 1 and '`' in text):
        raise OSError('the body is built by a command substitution: pass a literal path')
    return [text]


def effective_cwd(code: str, cwd: str) -> str:
    for m in CD.finditer(code):
        cwd = os.path.join(cwd, m.group(1))
    return cwd


def describe(problems: list[Problem]) -> str:
    shown = '; '.join(
        f'L{p.line} {p.text}' if p.line else p.text for p in problems[:SHOWN_PROBLEMS]
    )
    more = len(problems) - SHOWN_PROBLEMS
    return shown + (f' (+{more} more)' if more > 0 else '')


def find_posts(code: str) -> list[tuple[int, Kind, bool]]:
    """(position, kind, body required) per gh invocation that posts, in command order."""
    hits = {}
    for pattern, kind, required in POSTS:
        for m in pattern.finditer(code):
            hits.setdefault(m.start('gh'), (kind, required))
    return [(at, *hits[at]) for at in sorted(hits)]


def segment_reason(
    segment: str, docs: list[str], cwd: str, kind: Kind, required: bool
) -> str | None:
    try:
        bodies = read_bodies(segment, docs, cwd)
    except OSError as err:
        return str(err)
    if not bodies:
        if not required:
            return None
        return (
            f'{kind.value} body not found in the command: write it with the {SKILL[kind]} skill,'
            f' lint it, and pass --body-file <path>'
        )
    title = TITLE.search(segment)
    for body in bodies:
        problems = lint(kind, body, quoted(title) if title and kind is Kind.PR else None)
        if problems:
            return (
                f'GitHub {kind.value} text refused: {describe(problems)}. Fix it per the'
                f' {SKILL[kind]} skill: python3 ~/.claude/hooks/gh_text_lint.py {kind.value} <file>'
            )
    return None


def command_reason(command: str, cwd: str | None = None) -> str | None:
    """Why a gh command that posts text must not run, or None when it may."""
    code, docs = mark_heredocs(command)
    posts = find_posts(code)
    ends = [at for at, _, _ in posts[1:]] + [len(code)]
    for (at, kind, required), end in zip(posts, ends):
        try:
            reason = segment_reason(
                code[at:end], docs, effective_cwd(code[:at], cwd or os.getcwd()), kind, required
            )
        except Exception as err:
            return (
                f'the GitHub text gate failed on this command ({err!r}): fix gh_text_lint.py first'
            )
        if reason:
            return reason
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
