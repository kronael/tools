#!/usr/bin/env python3
"""Lint text bound for GitHub: a PR body, an issue body or a review comment.

WISDOM § Git and the posting skill's Format section are the rules; this is
the part of them a program can check. pretool_nudge.py calls `command_reason`
to refuse a `gh` command whose body fails, and a review submit the newest
message the user typed did not ask for with the words SUBMIT REVIEW.

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
import shlex
import sys
from dataclasses import dataclass
from enum import Enum


class Kind(str, Enum):
    PR = 'pr'
    ISSUE = 'issue'
    COMMENT = 'comment'


class Action(str, Enum):
    NONE = 'none'
    SUBMIT = 'submit'
    APPROVE = 'approve'
    MERGE = 'merge'


@dataclass(frozen=True)
class Problem:
    """A lint failure; `line` is 0 when it is not bound to one line."""

    line: int
    text: str


ROBOT = '\U0001f916'
TLDR = '**TL;DR:**'
SKILL = {Kind.PR: 'pr-draft', Kind.ISSUE: 'gh-issue', Kind.COMMENT: 'gh-comment'}
MAX_CHARS = {Kind.PR: 1000, Kind.ISSUE: 3000, Kind.COMMENT: 240}
MAX_LEAD = 400
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

PREFIX = (
    r'(?:\w+=\S*[ \t]+)*'
    r'(?:(?:env|command|exec|timeout|sudo|nice|nohup)[ \t]+(?:\S+[ \t]+)*?)?'
    r'(?:\S*/)?'
)
GH_OPTIONS = r'(?:[ \t]+(?:--repo[ =]|-R[ \t]*)\S+)*\s+'
REPO_OPTIONS = r'(?:[ \t]+(?:--repo[ =]|-R[ \t]*)\S+)*\s+'
GH = (
    r'(?:^|[;&|({\n!]|\$\(|\b(?:if|then|else|elif|do|while|until)\s)\s*'
    + PREFIX
    + r'(?P<gh>gh'
    + GH_OPTIONS
)
API = GH + r"""api\b(?:[^'"\n|;&]|'[^']*'|"(?:[^"\\]|\\.)*")*(?:['"][^\s'"]*)?"""
GRAPHQL_ENDPOINT = r"""(?:https?://[^\s/'"]+)?/?graphql/?(?:\?[^\s'"]*)?"""
POSTS = (
    (re.compile(GH + r'pr\s+create\b)'), Kind.PR, True),
    (re.compile(GH + r'pr\s+edit\b)'), Kind.PR, False),
    (re.compile(GH + r'issue\s+create\b)'), Kind.ISSUE, True),
    (re.compile(GH + r'issue\s+edit\b)'), Kind.ISSUE, False),
    (re.compile(GH + r'(?:pr|issue)\s+comment\b)'), Kind.COMMENT, True),
    (re.compile(GH + r'pr' + REPO_OPTIONS + r'review\b)'), Kind.COMMENT, False),
    (re.compile(API + r'(?:/reviews|/comments|/replies)\b)'), Kind.COMMENT, False),
    (re.compile(API + r'\b(?:add|submit)PullRequestReview\b)'), Kind.COMMENT, False),
    (re.compile(API + r'\bpulls/\d+(?![\w/]))'), Kind.PR, False),
    (re.compile(API + r'\bissues/\d+(?![\w/]))'), Kind.ISSUE, False),
)
SUBMIT_ASK = 'SUBMIT REVIEW'
CLI_REVIEW = re.compile(r'^gh' + GH_OPTIONS + r'pr' + REPO_OPTIONS + r'review\b')
API_REVIEW = re.compile(r'/pulls/[^/\s]+/reviews(?:/[^/\s]+/events)?/?(?:\?\S*)?$')
GRAPHQL_REVIEW = re.compile(r'\b(?:submit|add)PullRequestReview\s*\(')
USER = b'"user"'
TOOL_RESULT = b'"content":[{"type":"tool_result"'
SUBMIT_REFUSED = (
    f'review submit refused: the newest message the user typed does not say {SUBMIT_ASK}.'
    ' A submitted review cannot be taken back: leave it PENDING, report its id and ask'
    f' the user to say {SUBMIT_ASK} (gh-comment § Submit)'
)
HEREDOC = re.compile(r"""(?<!<)<<(?!<)-?[ \t]*((?:\w+|'[^']*'|"[^"]*"|\\.)+)[^\n]*\n""")
CONTINUATION = re.compile(r'\\\n')
MARK = '\x00'
MARKED = re.compile(f'{MARK}(\\d+){MARK}')
CD = re.compile(r'(?:^|[;&|(\n]|\b(?:then|do)\s)\s*cd\s+([^\s;&|)]+)')
QUOTED = r'(?:"((?:[^"\\]|\\.)*)"|\'([^\']*)\'|([^\s;&|)]+))'
INPUT = re.compile(r'--input[ =]' + QUOTED)
BODY_FILE = re.compile(
    r'(?:--body-file[ =]|(?:-F|--field)\s+body=@|(?<!\S)-F\s+(?!["\']?[\w\[\]-]+=))' + QUOTED
)
BODY_TEXT = re.compile(
    r'(?:--body[ =]|(?<!\S)-b\s+|(?:-f|-F|--field|--raw-field)\s+body=)' + QUOTED
)
TITLE = re.compile(r'(?:--title[ =]|(?<!\S)-t\s+)' + QUOTED)
CAT_FILE = re.compile(r'^\$\(\s*cat\s+' + QUOTED + r'\s*\)$')
CAT_HEREDOC = re.compile(r'^\$\(\s*cat\s*<<')
JSON_BODY = re.compile(r'"body"\s*:\s*"((?:[^"\\]|\\.)*)"')


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
    lead = re.split(r'\n\s*\n', '\n'.join(lines).lstrip(), maxsplit=1)[0]
    if len(lead) > MAX_LEAD:
        problems.append(
            Problem(1, f'TL;DR {len(lead)} chars, cap {MAX_LEAD}: move context below the lead')
        )
    for n, line in enumerate(lines, 1):
        if THIS_PR.search(line):
            problems.append(Problem(n, '"this PR": name what the change does instead'))
    return problems


def lint_title(title: str) -> list[Problem]:
    problems = []
    if len(title) > MAX_TITLE:
        problems.append(Problem(0, f'title {len(title)} chars, max {MAX_TITLE}'))
    if title.count(' and ') >= 2:
        problems.append(Problem(0, 'title lists changes: name the one outcome above them'))
    return problems


def lint(kind: Kind, text: str, title: str | None = None) -> list[Problem]:
    body = text.rstrip()
    if not body:
        return [Problem(0, 'empty body')]
    lines = body.split('\n')
    problems = lint_common(kind, lines, body)
    problems += lint_opener(lines)
    if kind is Kind.PR:
        problems += lint_pr(lines)
    if title is not None:
        problems += lint_title(title)
    return problems


def mark_heredocs(command: str) -> tuple[str, list[str]]:
    """The command with each heredoc's content replaced by a marker, and the contents."""
    docs = []

    parts = []
    offset = 0
    while match := HEREDOC.search(command, offset):
        delimiter = shlex.split(match.group(1))[0]
        end = re.search(
            r'(?m)^[ \t]*' + re.escape(delimiter) + r'[ \t]*(?:\n|$)', command[match.end() :]
        )
        if not end:
            break
        body_end = match.end() + end.start()
        body = command[match.end() : body_end].removesuffix('\n')
        docs.append(body)
        parts.append(command[offset : match.end()])
        parts.append(f'{MARK}{len(docs) - 1}{MARK}\n')
        offset = body_end
    parts.append(command[offset:])
    return ''.join(parts), docs


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
    if not m:
        return None
    return docs[int(m.group(1))]


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


def graphql_review_bodies(segment: str, data: dict | None, cwd: str) -> list[str]:
    query = data.get('query', '') if data else ''
    bodies = []
    tokens = shlex.split(segment)
    for index, token in enumerate(tokens):
        if token in {'-f', '-F', '--field', '--raw-field'} and index + 1 < len(tokens):
            field = tokens[index + 1]
        elif token.startswith(('-fquery=', '-Fquery=')):
            field = token[2:]
        elif token.startswith(('--field=query=', '--raw-field=query=')):
            field = token.partition('=')[2]
        else:
            continue
        if field.startswith('query='):
            query = field.partition('=')[2]
            typed = token in {'-F', '--field'} or token.startswith(('-F', '--field='))
            if typed and query.startswith('@'):
                query = read_file(query[1:], cwd)
        elif data is None and re.match(r'(?:\w+\[)+body\]=', field):
            value = field.partition('=')[2]
            typed = token in {'-F', '--field'} or token.startswith(('-F', '--field='))
            bodies.append(read_file(value[1:], cwd) if typed and value.startswith('@') else value)
    if not isinstance(query, str) or not GRAPHQL_REVIEW.search(query):
        return []
    delimiters = re.sub(
        r'"""[\s\S]*?"""|"(?:[^"\\]|\\.)*"|#[^\n]*',
        lambda m: ' ' * len(m.group()),
        query,
    )
    if '"' in delimiters:
        raise OSError('cannot inspect GraphQL strings')
    for review in GRAPHQL_REVIEW.finditer(delimiters):
        depth = 1
        end = review.end()
        while end < len(delimiters) and depth:
            depth += (delimiters[end] == '(') - (delimiters[end] == ')')
            end += 1
        if depth:
            raise OSError('cannot inspect GraphQL review arguments')
        args = query[review.end() : end - 1]
        masked_args = delimiters[review.end() : end - 1]
        for field in re.finditer(r'\bbody\s*:', masked_args):
            if not args[field.end() :].lstrip().startswith('"'):
                raise OSError('cannot inspect GraphQL review body')
        bodies.extend(
            json.loads(match.group(1))
            for match in re.finditer(r'\bbody\s*:\s*("(?:[^"\\]|\\.)*")', args)
        )
    return bodies


def read_bodies(segment: str, docs: list[str], cwd: str) -> list[str]:
    """Every body text the segment posts; OSError names a body it cannot read."""
    doc = heredoc_in(segment, docs)
    given = input_json(segment, docs, cwd)
    if given is not None:
        data = json.loads(given)
        return json_bodies(given) + graphql_review_bodies(
            segment, data if isinstance(data, dict) else None, cwd
        )
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
        return graphql_review_bodies(segment, None, cwd) if 'graphql' in segment else []
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


def github_action(segment: str, docs: list[str], cwd: str) -> Action:
    values = []
    parts = []
    offset = 0
    for match in re.finditer(r"""'[^']*'|"(?:\\[\s\S]|[^"\\])*"|\\[\s\S]""", segment):
        parts.append(segment[offset : match.start()])
        parts.append(f'\x00q{len(values)}\x00')
        values.append(shlex.split(match.group())[0])
        offset = match.end()
    parts.append(segment[offset:])
    lexer = shlex.shlex(''.join(parts), posix=True, punctuation_chars=';&|\n')
    lexer.whitespace = ' \t\r'
    lexer.whitespace_split = True
    lexer.commenters = ''
    tokens = []
    for token in lexer:
        if token and not token.strip(';&|\n'):
            break
        word = token
        for index, value in enumerate(values):
            word = word.replace(f'\x00q{index}\x00', value)
        tokens.append(word)
    if re.match(r'^gh' + GH_OPTIONS + r'pr' + REPO_OPTIONS + r'merge\b', segment):
        words = iter(tokens)
        for word in words:
            if word in {'--subject', '-t', '--body', '-b', '--author-email', '--repo', '-R'}:
                next(words, None)
            elif word in {'--help', '-h', '--disable-auto'}:
                return Action.NONE
        return Action.MERGE
    if CLI_REVIEW.match(segment):
        findings = False
        approval = False
        help_requested = False
        words = iter(tokens)
        for word in words:
            if word in {'--body', '-b', '--body-file', '-F', '--repo', '-R'}:
                next(words, None)
                continue
            if word.startswith(('--body=', '--body-file=', '--repo=', '-R')):
                continue
            help_requested |= word in {'--help', '-h'}
            approval |= word == '--approve' or word.startswith('--approve=')
            if word.startswith('-') and not word.startswith('--'):
                flags = word[1:].split('b', 1)[0]
                approval |= 'a' in flags
                findings |= bool(set(flags) & {'c', 'r'})
            findings |= word in {
                '--comment',
                '--request-changes',
                '--comment=true',
                '--request-changes=true',
            }
        if help_requested:
            return Action.NONE
        return Action.SUBMIT if findings and not approval else Action.APPROVE
    if not re.match(r'^gh' + GH_OPTIONS + r'api\b', segment):
        return Action.NONE
    graphql = any(re.fullmatch(GRAPHQL_ENDPOINT, t) for t in tokens)
    endpoint = next((t for t in tokens if API_REVIEW.search(t)), '')
    merge = next(
        (t for t in tokens if re.search(r'/pulls/[^/\s]+/merge(?:-async)?/?(?:\?\S*)?$', t)), ''
    )
    if not graphql and not endpoint and not merge:
        return Action.NONE
    fields = {}
    method = ''
    words = iter(tokens)
    for token in words:
        if token in {'--help', '-h'}:
            return Action.NONE
        if token in {'--method', '-X'}:
            method = next(words, '')
        elif token in {
            '--cache',
            '--header',
            '-H',
            '--hostname',
            '--input',
            '--jq',
            '-q',
            '--preview',
            '-p',
            '--template',
            '-t',
        }:
            next(words, None)
        elif token.startswith('--method='):
            method = token.partition('=')[2]
        elif token.startswith('-X'):
            method = token[2:]
        elif token in {'-f', '-F', '--field', '--raw-field'}:
            raw = token in {'-f', '--raw-field'}
            field = next(words, '')
            key, _, value = field.partition('=')
            fields[key] = read_file(value[1:], cwd) if not raw and value.startswith('@') else value
        elif token.startswith(('--field=', '--raw-field=', '-f', '-F')):
            raw = token.startswith(('--raw-field=', '-f'))
            field = token.partition('=')[2] if token.startswith('--') else token[2:]
            key, _, value = field.partition('=')
            fields[key] = read_file(value[1:], cwd) if not raw and value.startswith('@') else value
    if method.upper() in {'GET', 'HEAD', 'OPTIONS', 'DELETE'}:
        return Action.NONE
    if merge:
        return Action.MERGE if method.upper() == 'PUT' else Action.NONE
    if (
        not method
        and not fields
        and '--input' not in tokens
        and not any(t.startswith('--input=') for t in tokens)
    ):
        return Action.NONE
    text = input_json(segment, docs, cwd)
    try:
        data = json.loads(text) if text is not None else {}
    except json.JSONDecodeError as err:
        raise OSError(f'cannot parse the JSON body: {err}') from err
    if not isinstance(data, dict):
        raise OSError('cannot inspect the review JSON: pass an object')
    if text is not None:
        fields = {}
    if not graphql:
        event = fields.get('event', data.get('event'))
        if event == 'APPROVE':
            return Action.APPROVE
        if event is not None and event not in ('COMMENT', 'REQUEST_CHANGES', 'DISMISS'):
            raise OSError('cannot inspect the review event: pass a literal event')
        return Action.SUBMIT if event is not None or '/events' in endpoint else Action.NONE

    query = fields.get('query', data.get('query', ''))
    if not isinstance(query, str):
        raise OSError('cannot inspect the GraphQL query: pass literal query text')
    query = re.sub(r'"""[\s\S]*?"""|"(?:[^"\\]|\\.)*"|#[^\n]*', '', query)
    if not re.search(r'^\s*(?:\{|(?:query|mutation|subscription)\b)', query):
        raise OSError('cannot inspect the GraphQL query: pass literal query text')
    if not re.search(r'\bmutation\b', query):
        return Action.NONE
    merge_mutation = bool(
        re.search(
            r'\b(?:mergePullRequest|enablePullRequestAutoMerge|enqueuePullRequest)\s*\(', query
        )
    )
    reviews = list(GRAPHQL_REVIEW.finditer(query))
    if not reviews:
        return Action.MERGE if merge_mutation else Action.NONE
    variables = data.get('variables', {})
    if not isinstance(variables, dict):
        raise OSError('cannot inspect GraphQL variables')
    result = Action.NONE
    for review in reviews:
        start = review.end()
        depth = 1
        end = start
        while end < len(query) and depth:
            depth += (query[end] == '(') - (query[end] == ')')
            end += 1
        if depth:
            raise OSError('cannot inspect GraphQL mutation arguments')
        args = query[start : end - 1]
        event_match = re.search(r'\bevent\s*:\s*(\$?\w+)', args)
        input_match = re.search(r'\binput\s*:\s*\$(\w+)', args)
        event = None
        if event_match:
            event = event_match.group(1)
            if event.startswith('$'):
                name = event[1:]
                default = re.search(
                    r'\$' + re.escape(name) + r'\s*:\s*[^=,)]+\s*=\s*(\w+)', query[: review.start()]
                )
                event = fields.get(name, variables.get(name, default.group(1) if default else None))
        elif input_match:
            name = input_match.group(1)
            value = variables.get(name, fields.get(name))
            if isinstance(value, dict):
                event = value.get('event')
            else:
                event = fields.get(f'{name}[event]', fields.get(f'variables[{name}][event]'))
                if event is None:
                    default = re.search(
                        r'\$' + re.escape(name) + r'\s*:\s*[^=,)]+\s*=\s*\{([^}]*)\}',
                        query[: review.start()],
                    )
                    if default:
                        default_event = re.search(r'\bevent\s*:\s*(\w+)', default.group(1))
                        event = default_event.group(1) if default_event else None
                    else:
                        raise OSError('cannot inspect GraphQL review input')
        elif not re.search(r'\binput\s*:\s*\{', args):
            raise OSError('cannot inspect GraphQL review input')
        if event == 'APPROVE':
            result = Action.APPROVE
        elif event is not None and event not in ('COMMENT', 'REQUEST_CHANGES', 'DISMISS'):
            raise OSError('cannot inspect GraphQL review event')
        elif result is Action.NONE and (event is not None or review.group().startswith('submit')):
            result = Action.SUBMIT
    return Action.MERGE if merge_mutation else result


def iter_lines_reversed(path: str, chunk: int = 1 << 16):
    with open(path, 'rb') as fh:
        fh.seek(0, os.SEEK_END)
        pos = fh.tell()
        tail = b''
        while pos > 0:
            step = min(chunk, pos)
            pos -= step
            fh.seek(pos)
            lines = (fh.read(step) + tail).split(b'\n')
            tail = lines[0]
            yield from reversed(lines[1:])
        yield tail


def prompt_text(line: bytes) -> str | None:
    """The text of a transcript record the user typed, else None: a tool
    result, hook feedback (isMeta), a subagent's thread (isSidechain) and a
    task notification (origin.kind) are not the user's words."""
    if USER not in line or TOOL_RESULT in line:
        return None
    try:
        record = json.loads(line)
    except ValueError:
        return None
    if not isinstance(record, dict) or record.get('type') != 'user':
        return None
    if record.get('isMeta') or record.get('isSidechain'):
        return None
    origin = record.get('origin')
    if isinstance(origin, dict) and origin.get('kind') != 'human':
        return None
    message = record.get('message')
    content = message.get('content') if isinstance(message, dict) else None
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return None
    blocks = [b for b in content if isinstance(b, dict)]
    if any(b.get('type') == 'tool_result' for b in blocks):
        return None
    return '\n'.join(str(b.get('text', '')) for b in blocks if b.get('type') == 'text')


def latest_prompt(transcript_path: str | None) -> str:
    """The newest message the user typed, read from the end of the session
    transcript; '' when there is none or the transcript cannot be read."""
    if not transcript_path:
        return ''
    try:
        for line in iter_lines_reversed(transcript_path):
            text = prompt_text(line)
            if text is not None:
                return text
    except OSError:
        return ''
    return ''


def describe(problems: list[Problem]) -> str:
    shown = '; '.join(
        f'L{p.line} {p.text}' if p.line else p.text for p in problems[:SHOWN_PROBLEMS]
    )
    more = len(problems) - SHOWN_PROBLEMS
    return shown + (f' (+{more} more)' if more > 0 else '')


def quoted_spans(code: str) -> list[tuple[int, int]]:
    return [(m.start(), m.end()) for m in re.finditer(r"\"(?:\\[\s\S]|[^\"\\])*\"|'[^']*'", code)]


def find_posts(code: str) -> list[tuple[int, Kind, bool]]:
    """(position, kind, body required) per gh invocation that posts, in command order."""
    hits = {}
    spans = quoted_spans(code)
    for pattern, kind, required in POSTS:
        for m in pattern.finditer(code):
            if not any(start < m.start('gh') < end for start, end in spans):
                hits.setdefault(m.start('gh'), (kind, required))
    return [(at, *hits[at]) for at in sorted(hits)]


def segment_reason(
    segment: str,
    docs: list[str],
    cwd: str,
    kind: Kind,
    required: bool,
    transcript_path: str | None = None,
) -> str | None:
    try:
        action = github_action(segment, docs, cwd)
        bodies = read_bodies(segment, docs, cwd)
    except OSError as err:
        return str(err)
    if not bodies:
        if not required:
            if action is Action.SUBMIT and SUBMIT_ASK not in latest_prompt(transcript_path):
                return SUBMIT_REFUSED
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
    if action is Action.SUBMIT and SUBMIT_ASK not in latest_prompt(transcript_path):
        return SUBMIT_REFUSED
    return None


def shell_substitutions(
    code: str, docs: list[str] | None = None, *, heredoc: bool = False
) -> tuple[str, list[tuple[int, str]]]:
    substitutions = []
    masked = list(code)
    index = 0
    quote = ''
    while index < len(code):
        char = code[index]
        marker = MARKED.match(code, index) if docs is not None else None
        if marker:
            line_start = code.rfind('\n', 0, index - 1) + 1
            header = HEREDOC.search(code, line_start, index)
            if header and not any(c in header.group(1) for c in '\'"\\'):
                _, nested = shell_substitutions(docs[int(marker.group(1))], heredoc=True)
                substitutions.extend((index, body) for _, body in nested)
            index = marker.end()
            continue
        if not heredoc and char == "'" and quote != '"':
            quote = '' if quote == "'" else "'"
        elif not heredoc and char == '"' and quote != "'":
            quote = '' if quote == '"' else '"'
        elif char == '\\' and quote != "'":
            index += 2
            continue
        elif (
            not heredoc
            and char == '#'
            and not quote
            and (index == 0 or code[index - 1] in ' \t\n;&|(')
        ):
            end = code.find('\n', index)
            index = len(code) if end < 0 else end
            continue
        elif quote != "'" and (code.startswith('$(', index) or char == '`'):
            start = index
            backtick = char == '`'
            index += 1 if backtick else 2
            body_start = index
            depth = 1
            inner_quote = ''
            while index < len(code):
                inner = code[index]
                if inner == '\\' and inner_quote != "'":
                    index += 2
                    continue
                if (
                    inner == '#'
                    and not inner_quote
                    and (index == body_start or code[index - 1] in ' \t\n;&|(')
                ):
                    newline = code.find('\n', index)
                    index = len(code) if newline < 0 else newline
                    continue
                if backtick:
                    if inner == '`':
                        break
                elif inner == "'" and inner_quote != '"':
                    inner_quote = '' if inner_quote == "'" else "'"
                elif inner == '"' and inner_quote != "'":
                    inner_quote = '' if inner_quote == '"' else '"'
                elif not inner_quote and inner == '(':
                    depth += 1
                elif not inner_quote and inner == ')':
                    depth -= 1
                    if not depth:
                        break
                index += 1
            if index >= len(code):
                raise OSError('cannot inspect an incomplete command substitution')
            substitutions.append((start, code[body_start:index]))
            for offset in range(start, index + 1):
                if masked[offset] != '\n':
                    masked[offset] = ' '
        index += 1
    return ''.join(masked), substitutions


def command_reason(
    command: str, cwd: str | None = None, transcript_path: str | None = None
) -> str | None:
    """Why a gh command that posts text must not run, or None when it may: a
    body that fails the lint, or a review submit the newest message the user
    typed (in the transcript at `transcript_path`) did not ask for."""
    try:
        code, docs = mark_heredocs(command)
        code = CONTINUATION.sub('', code)
        masked, substitutions = shell_substitutions(code, docs)
        for at, nested in substitutions:
            expanded = MARKED.sub(lambda m: docs[int(m.group(1))], nested)
            reason = command_reason(
                expanded, effective_cwd(code[:at], cwd or os.getcwd()), transcript_path
            )
            if reason:
                return reason
        posts = find_posts(code)
        if substitutions and not any(at < substitutions[0][0] for at, _, _ in posts):
            code = masked
            posts = find_posts(code)
        ends = [at for at, _, _ in posts[1:]] + [len(code)]
        for (at, kind, required), end in zip(posts, ends):
            reason = segment_reason(
                code[at:end],
                docs,
                effective_cwd(code[:at], cwd or os.getcwd()),
                kind,
                required,
                transcript_path,
            )
            if reason:
                return reason
        spans = quoted_spans(code)
        for match in re.finditer(GH + r'api\b)', code):
            at = match.start('gh')
            if any(start < at < end for start, end in spans):
                continue
            segment = code[at:]
            if not re.search(r'\bgraphql\b', segment):
                continue
            workdir = effective_cwd(code[:at], cwd or os.getcwd())
            text = input_json(segment, docs, workdir)
            data = json.loads(text) if text is not None else {}
            query = data.get('query', segment) if isinstance(data, dict) else segment
            review_bodies = graphql_review_bodies(
                segment, data if isinstance(data, dict) else None, workdir
            )
            action = github_action(segment, docs, workdir)
            if (
                review_bodies
                or action in {Action.APPROVE, Action.SUBMIT}
                or (
                    isinstance(query, str)
                    and re.search(r'\bmutation\b', query)
                    and GRAPHQL_REVIEW.search(query)
                )
            ):
                reason = segment_reason(
                    segment, docs, workdir, Kind.COMMENT, False, transcript_path
                )
                if reason:
                    return reason
    except Exception as err:
        return f'the GitHub text gate failed on this command ({err!r}): fix gh_text_lint.py first'
    return None


def command_action(command: str, cwd: str | None = None) -> Action:
    """Classify the visible GitHub actions in a command."""
    code, docs = mark_heredocs(command)
    code = CONTINUATION.sub('', code)
    code, substitutions = shell_substitutions(code, docs)
    result = Action.NONE
    for at, nested in substitutions:
        expanded = MARKED.sub(lambda m: docs[int(m.group(1))], nested)
        action = command_action(expanded, effective_cwd(code[:at], cwd or os.getcwd()))
        if action is Action.MERGE:
            return action
        if action is Action.APPROVE or (action is Action.SUBMIT and result is Action.NONE):
            result = action
    code = re.sub(
        r"""'[^']*'|"(?:\\[\s\S]|[^"\\])*"|\\[\s\S]|(?<![^\s;&|()])#[^\n]*""",
        lambda m: '' if m.group().startswith('#') else m.group(),
        code,
    )
    spans = quoted_spans(code)
    matches = [
        m
        for m in re.finditer(GH + r')', code)
        if not any(start < m.start('gh') < end for start, end in spans)
    ]
    for match in matches:
        action = github_action(
            code[match.start('gh') :],
            docs,
            effective_cwd(code[: match.start('gh')], cwd or os.getcwd()),
        )
        if action is Action.MERGE:
            return action
        if action is Action.APPROVE or (action is Action.SUBMIT and result is Action.NONE):
            result = action
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description='Lint text bound for GitHub')
    parser.add_argument('kind', choices=[k.value for k in Kind])
    parser.add_argument('file')
    parser.add_argument('--draft', help='the first version, for an informational size comparison')
    parser.add_argument('--title', help='the PR title to check beside the body')
    args = parser.parse_args()
    with open(args.file, encoding='utf-8') as fh:
        text = fh.read()
    draft = None
    if args.draft:
        with open(args.draft, encoding='utf-8') as fh:
            draft = fh.read()
    problems = lint(Kind(args.kind), text, args.title)
    for p in problems:
        where = f'{args.file}:{p.line}' if p.line else args.file
        print(f'{where}: {p.text}')
    if problems:
        print(f'fail: {len(problems)} problem(s)')
        return 1
    n = len(text.rstrip())
    draft_size = len(draft.rstrip()) if draft is not None else 0
    cut = f', draft {draft_size} -> {100 * n // draft_size}%' if draft_size else ''
    print(f'ok: {args.kind} {n} chars{cut}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
