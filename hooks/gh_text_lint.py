#!/usr/bin/env python3
"""Lint text bound for GitHub: a PR body, an issue body or a review comment.

WISDOM § Git and the posting skill's Format section are the rules; this is
the part of them a program can check. pretool_nudge.py calls
`command_decision` to deny a `gh` command whose body fails and to raise the
permission dialog on a review submit, which cannot be taken back.

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
from dataclasses import replace
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


class Permission(str, Enum):
    DENY = 'deny'
    ASK = 'ask'


@dataclass(frozen=True)
class Decision:
    """What a gh command needs before it runs: `deny` with the reason Claude
    reads, or `ask` with the reason the permission dialog shows the user."""

    permission: Permission
    reason: str


ROBOT = '\U0001f916'
TLDR = '**TL;DR:**'
SKILL = {Kind.PR: 'pr-draft', Kind.ISSUE: 'gh-issue', Kind.COMMENT: 'gh-comment'}
MAX_CHARS = {Kind.PR: 1800, Kind.ISSUE: 3000, Kind.COMMENT: 240}
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
HEADER = re.compile(r'^\s*(?:[-*+]\s+)?#{1,6}\s')
RULE = re.compile(r'^\s*(?:-{3,}|\*{3,}|_{3,})\s*$')
TABLE = re.compile(r'^\s*\|')
CHECKBOX = re.compile(r'^\s*[-*+]\s+\[[ xX]\]')
IMAGE = re.compile(r'!\[[^\]]*\]\(')
BULLET = re.compile(r'^\s*[-*+]\s')
CLOSER = re.compile(r'^(?:[Cc]los\w*|[Ff]ix\w*|[Rr]esolv\w*) #\d+')
FENCE = re.compile(r'^\s*(?:```|~~~)')

PREFIX = (
    r'(?:\w+=\S*[ \t]+)*'
    r'(?:(?:env|command|exec|timeout|sudo|nice|nohup)[ \t]+(?:\S+[ \t]+)*?)?'
    r'(?:\S*/)?'
)
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
    (re.compile(API + r'\bsubmitPullRequestReview\b)'), Kind.COMMENT, False),
    (re.compile(API + r'\bpulls/\d+(?![\w/]))'), Kind.PR, False),
    (re.compile(API + r'\bissues/\d+(?![\w/]))'), Kind.ISSUE, False),
)
SUBMIT_REASON = (
    'Submits the review: it reaches the PR at once and cannot be taken back (gh-comment § Submit)'
)
ARGS = r'[^\n|;&]*'
SUBMITS = (
    re.compile(r'^gh\s+pr\s+review\b'),
    re.compile(r'^gh\s+api\b' + ARGS + r'/reviews/[^/\s]+/events\b'),
    re.compile(r'^gh\s+api\b' + ARGS + r'\bsubmitPullRequestReview\b'),
)
REVIEWS = re.compile(r'^gh\s+api\b' + ARGS + r'/reviews(?![\w/])')
EVENT_FLAG = re.compile(r'(?:-f|-F|--field|--raw-field)[ =]["\']?event=')
HEREDOC = re.compile(r'<<-?\s*([\'"]?)(\w+)\1[^\n]*\n(.*?)\n[ \t]*\2[ \t]*(?:\n|$)', re.DOTALL)
CONTINUATION = re.compile(r'\\\n')
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
    return [(n, line) for n, line, fenced in walk(lines) if not fenced]


def walk(lines: list[str]) -> list[tuple[int, str, bool]]:
    out = []
    fenced = False
    for n, line in enumerate(lines, 1):
        if FENCE.match(line):
            fenced = not fenced
        else:
            out.append((n, line, fenced))
    return out


@dataclass(frozen=True)
class Element:
    """One unit of a PR body: the lead, a closer, or a stray bullet or
    paragraph, with its continuation lines joined."""

    line: int
    kind: str
    text: str


def split_elements(prose: list[tuple[int, str]]) -> list[Element]:
    out: list[Element] = []
    after_blank = True
    for n, line in prose:
        text = line.strip()
        if not text:
            after_blank = True
            continue
        starts = BULLET.match(line) or CLOSER.match(line)
        if out and not after_blank and not starts:
            out[-1] = replace(out[-1], text=f'{out[-1].text} {text}')
        elif BULLET.match(line):
            out.append(Element(n, 'bullet', text))
        elif CLOSER.match(line):
            out.append(Element(n, 'closer', text))
        elif not out:
            out.append(Element(n, 'lead', text))
        else:
            out.append(Element(n, 'paragraph', text))
        after_blank = False
    return out


def lint_common(kind: Kind, lines: list[str], body: str) -> list[Problem]:
    problems = []
    for n, line in enumerate(lines, 1):
        lower = line.lower()
        problems += [
            Problem(n, f'banned attribution "{b}": the only attribution is the opening "{ROBOT} "')
            for b in BANNED
            if b in lower
        ]
        if ELLIPSIS in line or SHORTENED.search(line):
            problems.append(Problem(n, 'shortened address, hash or sentence: write it in full'))
        problems += [Problem(n, f'marketing word "{m.group()}"') for m in MARKETING.finditer(line)]
    if len(body) > MAX_CHARS[kind]:
        problems.append(Problem(0, f'{len(body)} chars, cap {MAX_CHARS[kind]}: cut, or link a doc'))
    return problems


def lint_opener(lines: list[str]) -> list[Problem]:
    start = next((n for n, line in enumerate(lines, 1) if line.strip()), 1)
    has_opener = lines[start - 1].startswith(ROBOT + ' ')
    problems = [] if has_opener else [Problem(start, f'must start with "{ROBOT} "')]
    for n, line in enumerate(lines, 1):
        if line.count(ROBOT) > (1 if has_opener and n == start else 0):
            problems.append(Problem(n, f'{ROBOT} belongs at the start only'))
    return problems


def lint_pr(lines: list[str]) -> list[Problem]:
    problems = []
    first = next((line for line in lines if line.strip()), '')
    if not first.removeprefix(ROBOT + ' ').startswith(TLDR):
        problems.append(Problem(1, f'open with {TLDR} and the outcome, not a header or narrative'))
    for n, line in enumerate(lines, 1):
        if CHECKBOX.match(line):
            problems.append(Problem(n, 'checkbox: no test plan or checklist'))
        if THIS_PR.search(line):
            problems.append(Problem(n, '"this PR": name what the change does instead'))
        if IMAGE.search(line):
            problems.append(Problem(n, 'image: link it instead'))
    prose = []
    for n, line in split_prose(lines):
        if HEADER.match(line):
            problems.append(Problem(n, 'header: the body is the TL;DR, no sections'))
        elif RULE.match(line):
            problems.append(Problem(n, 'horizontal rule'))
        elif TABLE.match(line):
            problems.append(Problem(n, 'table: cut it or fold it into the TL;DR'))
        else:
            prose.append((n, line))
    fence = next((n for n, line in enumerate(lines, 1) if FENCE.match(line)), 0)
    if fence:
        problems.append(
            Problem(fence, 'code block: the diff shows code, the TL;DR says what it does')
        )
    return problems + lint_elements(split_elements(prose))


def lint_elements(elements: list[Element]) -> list[Problem]:
    problems = []
    bullets = 0
    for e in elements:
        if e.kind == 'bullet':
            bullets += 1
            if bullets > 3:
                problems.append(Problem(e.line, 'review pointers: keep at most three bullets'))
        elif e.kind == 'paragraph':
            problems.append(
                Problem(
                    e.line,
                    'text after the lead: use up to three review pointers;'
                    ' fold other context into the TL;DR',
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
    problems += lint_opener(lines)
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


def input_json(segment: str, docs: list[str], cwd: str) -> str | None:
    """The JSON text `--input` passes, from its file or heredoc; None without it."""
    given = INPUT.search(segment)
    if not given:
        return None
    path = quoted(given)
    if path != '-':
        return read_file(path, cwd)
    doc = heredoc_in(segment, docs)
    if doc is None:
        raise OSError('--input - reads stdin the hook cannot see: pass a file or a heredoc')
    return doc


def read_bodies(segment: str, docs: list[str], cwd: str) -> list[str]:
    """Every body text the segment posts; OSError names a body it cannot read."""
    doc = heredoc_in(segment, docs)
    given = input_json(segment, docs, cwd)
    if given is not None:
        return json_bodies(given)
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
    raw = inline.group(1)
    unescaped = text if raw is None else re.sub(r'\\.', '', raw)
    if '$(' in unescaped or (raw is not None and '`' in unescaped):
        raise OSError('the body is built by a command substitution: pass a literal path')
    return [text]


def effective_cwd(code: str, cwd: str) -> str:
    for m in CD.finditer(code):
        cwd = os.path.join(cwd, m.group(1))
    return cwd


def has_event(text: str) -> bool:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as err:
        raise OSError(f'cannot parse the JSON body: {err}') from err
    return isinstance(data, dict) and 'event' in data


def is_submit(segment: str, docs: list[str], cwd: str) -> bool:
    """Whether the gh invocation submits a review: `gh pr review`, the
    `/reviews/<id>/events` call, a `/reviews` POST carrying `event`, or the
    submitPullRequestReview mutation. A pending post carries no `event`."""
    if any(p.match(segment) for p in SUBMITS):
        return True
    if not REVIEWS.match(segment):
        return False
    if EVENT_FLAG.search(segment):
        return True
    text = input_json(segment, docs, cwd)
    return text is not None and has_event(text)


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


def refusal(segment: str, docs: list[str], cwd: str, kind: Kind, required: bool) -> str | None:
    bodies = read_bodies(segment, docs, cwd)
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


def segment_decision(
    segment: str, docs: list[str], cwd: str, kind: Kind, required: bool
) -> Decision | None:
    try:
        refused = refusal(segment, docs, cwd, kind, required)
        submits = is_submit(segment, docs, cwd)
    except OSError as err:
        return Decision(Permission.DENY, str(err))
    if refused:
        return Decision(Permission.DENY, refused)
    if submits:
        return Decision(Permission.ASK, SUBMIT_REASON)
    return None


def command_decision(command: str, cwd: str | None = None) -> Decision | None:
    """What a gh command that posts text needs before it runs, or None when it
    may run: `deny` for a body that fails the lint or cannot be read, `ask` for
    a review submit. A deny in any gh invocation of the command wins over an
    ask in another."""
    asked = None
    try:
        code, docs = mark_heredocs(command)
        code = CONTINUATION.sub('', code)
        posts = find_posts(code)
        ends = [at for at, _, _ in posts[1:]] + [len(code)]
        for (at, kind, required), end in zip(posts, ends):
            decision = segment_decision(
                code[at:end], docs, effective_cwd(code[:at], cwd or os.getcwd()), kind, required
            )
            if decision is not None and decision.permission is Permission.DENY:
                return decision
            if asked is None:
                asked = decision
    except Exception as err:
        return Decision(
            Permission.DENY,
            f'the GitHub text gate failed on this command ({err!r}): fix gh_text_lint.py first',
        )
    return asked


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
