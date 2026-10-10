#!/usr/bin/env python3
import argparse
import json
import os
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timezone
from pathlib import Path

NOTE_RE = re.compile(r'<task-notification>(.*?)</task-notification>', re.DOTALL)
NOTE_FIELD_RE = re.compile(
    r'<(task-id|tool-use-id|status|summary|result|output-file)>(.*?)</\1>', re.DOTALL
)
SAVED_RE = re.compile(r'Full output saved to: (\S+)')
LIVE_RE = re.compile(r'Output is being written to: (\S+\.output)')
CMD_NAME_RE = re.compile(r'<command-name>/?(.*?)</command-name>', re.DOTALL)
CMD_ARGS_RE = re.compile(r'<command-args>(.*?)</command-args>', re.DOTALL)
CD_RE = re.compile(r'(?:^|[;&|(]|\bthen|\bdo)\s*cd\s+([^\s;&|)]+)')
GIT_C_RE = re.compile(r'\bgit\s+-C\s+([^\s;&|)]+)')
RECALL_RE = re.compile(
    r'(?<![\w.-])recall\.py\b|\.claude/projects/|/history\.jsonl|\.codex/sessions'
)
AGENT_ID_RE = re.compile(r'a[0-9a-f]{16}')
UUID_RE = re.compile(r'[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}')
LAUNCH_STUB = 'Async agent launched'
NOTICE_HEADS = ('<task-notification>', '[SYSTEM NOTIFICATION')
SKIP_PROMPTS = (
    '<local-command-stdout>',
    '<local-command-stderr>',
    '<local-command-caveat>',
    '<bash-stdout>',
    '<bash-stderr>',
    '<system-reminder>',
)
INPUT_KEYS = {
    'Bash': ['command'],
    'Agent': ['subagent_type', 'description'],
    'Task': ['subagent_type', 'description'],
    'Read': ['file_path'],
    'Edit': ['file_path'],
    'Write': ['file_path'],
    'NotebookEdit': ['notebook_path'],
    'Grep': ['pattern', 'path'],
    'Glob': ['pattern', 'path'],
    'Skill': ['skill', 'args'],
    'WebFetch': ['url'],
    'WebSearch': ['query'],
    'SendMessage': ['to', 'summary'],
}
EDIT_TOOLS = {'Edit', 'Write', 'MultiEdit', 'NotebookEdit'}
CODEX_SHELL_TOOLS = {'exec', 'exec_command', 'shell', 'shell_command'}
TOOL_GROUPS = {
    'bash': {'bash', 'commandexecution'} | CODEX_SHELL_TOOLS,
    'agent': {'agent', 'task', 'spawn_agent'},
}
SCOPED = {'sessions', 'results', 'prompts'}
VIEWER_WORDS = (
    '[ [[ awk basename cat cd column cut date df diff dirname du echo export file find grep '
    'head jq less ls nl printf ps pwd read readlink realpath rg sed set sleep sort stat tail '
    'test tr tree true uniq wait wc which'
)
VIEWERS = set(VIEWER_WORDS.split())
LOOP_HEADS = {'for', 'case', 'select'}
PREFIX_WORDS = {'do', 'done', 'then', 'else', 'elif', 'fi', 'esac', 'if', 'while', 'until', '!'}
QUOTED_RE = re.compile(r"'[^']*'|\"(?:[^\"\\]|\\.)*\"")
PART_RE = re.compile(r'\|\||&&|[;|\n(){}`]|\$\(')
ASSIGN_RE = re.compile(r'^\w+=')
BRACED_VAR_RE = re.compile(r'\$\{[^}]*\}')
HEREDOC_RE = re.compile(r'<<-?\s*[\'"]?(\w+)[\'"]?[^\n]*\n.*?\n\s*\1\b', re.DOTALL)


@dataclass
class Call:
    source: str
    session: str
    agent: str
    ts: str
    tool: str
    id: str
    inp: object
    path: str
    line: int
    cwd: str = ''
    output: str = ''
    error: bool = False
    status: str = ''
    note: str = ''
    task: str = ''
    saved: str = ''
    deep: bool = False


@dataclass
class Turn:
    ts: str
    prompt: str
    mid: bool = False
    replies: list[str] = field(default_factory=list)


@dataclass
class Note:
    ts: str
    text: str


@dataclass
class Transcript:
    source: str
    path: str
    session: str = ''
    agent: str = ''
    label: str = ''
    parent: str = ''
    title: str = ''
    ai_title: str = ''
    last_prompt: str = ''
    first: str = ''
    last: str = ''
    next: str = ''
    bad: int = 0
    cwds: set[str] = field(default_factory=set)
    branches: set[str] = field(default_factory=set)
    calls: list[Call] = field(default_factory=list)
    turns: list[Turn] = field(default_factory=list)
    compacts: list[Note] = field(default_factory=list)
    recaps: list[Note] = field(default_factory=list)
    prs: list[str] = field(default_factory=list)
    edited: dict[str, None] = field(default_factory=dict)
    notes: list[dict[str, str]] = field(default_factory=list)


@dataclass
class Homes:
    claude: Path
    codex: Path


@dataclass
class Query:
    terms: list[str]
    any_term: bool = False
    input_only: bool = False
    line: bool = False


def squash(text: str, width: int) -> str:
    flat = ' '.join(text.split())
    return flat if len(flat) <= width else flat[: width - 1] + '…'


def stamp(ts: str) -> str:
    return ts[:16].replace('T', ' ')


def matches(text: str, q: Query) -> bool:
    low = text.lower()
    if q.line and q.terms and not q.any_term:
        return any(all(t in row for t in q.terms) for row in low.splitlines())
    hits = [t in low for t in q.terms]
    return any(hits) if q.any_term and hits else all(hits)


def in_scope(cwds: set[str], roots: list[str] | None) -> bool:
    if roots is None:
        return True
    return any(c == r or c.startswith(r + '/') for r in roots for c in cwds)


def flatten(content: object) -> str:
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ''
    parts = []
    for b in content:
        if not isinstance(b, dict):
            continue
        kind = b.get('type')
        if kind in ('text', 'Text', 'input_text', 'output_text'):
            parts.append(b.get('text', ''))
        elif kind == 'tool_result':
            parts.append(flatten(b.get('content')))
        elif kind == 'image':
            parts.append('[image]')
        elif kind == 'tool_reference':
            parts.append(b.get('tool_name', ''))
    return '\n'.join(parts)


def render_input(tool: str, inp: object) -> str:
    if not isinstance(inp, dict):
        return str(inp)
    keys = INPUT_KEYS.get(tool, [])
    picked = [str(inp[k]) for k in keys if inp.get(k)]
    if picked:
        return ' '.join(picked)
    return json.dumps(inp, ensure_ascii=False)


def raw_input(c: Call) -> str:
    return c.inp if isinstance(c.inp, str) else json.dumps(c.inp, ensure_ascii=False)


def searchable(c: Call) -> str:
    return f'{c.tool}\n{raw_input(c)}\n{c.output}\n{c.note}'


def is_recall(c: Call) -> bool:
    if c.tool == 'Skill' and isinstance(c.inp, dict):
        return c.inp.get('skill') == 'recall-memories'
    return bool(RECALL_RE.search(raw_input(c)))


def is_run(c: Call) -> bool:
    tool = c.tool.lower()
    if tool in TOOL_GROUPS['agent']:
        return True
    if tool not in TOOL_GROUPS['bash']:
        return False
    command = c.inp.get('command', '') if isinstance(c.inp, dict) else str(c.inp)
    bare = BRACED_VAR_RE.sub('X', QUOTED_RE.sub(' ', HEREDOC_RE.sub(' ', str(command))))
    for part in PART_RE.split(bare):
        words = [w for w in part.split() if not ASSIGN_RE.match(w)]
        while words and words[0] in PREFIX_WORDS:
            words.pop(0)
        if not words or words[0] in LOOP_HEADS:
            continue
        if os.path.basename(words[0]) not in VIEWERS:
            return True
    return False


def agent_report(c: Call) -> str:
    return '' if c.output.startswith(LAUNCH_STUB) else c.output


def read_saved(c: Call) -> str:
    if not c.saved or not Path(c.saved).is_file():
        return ''
    return Path(c.saved).read_text(errors='replace')


def read_records(path: Path, t: Transcript):
    with path.open('rb') as f:
        for n, raw in enumerate(f, 1):
            try:
                r = json.loads(raw)
            except ValueError:
                t.bad += 1
                continue
            if isinstance(r, dict):
                yield n, r


def read_index(path: Path) -> list[dict]:
    rows = []
    bad = 0
    for line in path.read_text(errors='replace').splitlines():
        try:
            r = json.loads(line)
        except ValueError:
            bad += 1
            continue
        if isinstance(r, dict):
            rows.append(r)
    if bad:
        print(f'skipped {bad} malformed lines in {path}', file=sys.stderr)
    return rows


def mark_time(t: Transcript, ts: str) -> None:
    if not ts:
        return
    t.first = t.first or ts
    t.last = ts


def add_prompt(t: Transcript, ts: str, text: str, *, mid: bool = False) -> None:
    if text and not (t.turns and t.turns[-1].prompt == text):
        t.turns.append(Turn(ts, text, mid))


def add_reply(t: Transcript, ts: str, text: str) -> None:
    if not text.strip():
        return
    if not t.turns:
        t.turns.append(Turn(ts, ''))
    replies = t.turns[-1].replies
    if not replies or replies[-1] != text:
        replies.append(text)


def clean_prompt(text: str) -> str:
    s = text.strip()
    if not s or s.startswith(SKIP_PROMPTS):
        return ''
    name = CMD_NAME_RE.search(s)
    if name is None:
        return s
    args = CMD_ARGS_RE.search(s)
    return f'/{name.group(1)} {args.group(1) if args else ""}'.strip()


def parse_notes(text: str, ts: str) -> list[dict[str, str]]:
    found = []
    for block in NOTE_RE.findall(text):
        fields = {k: v.strip() for k, v in NOTE_FIELD_RE.findall(block)}
        found.append({**fields, 'ts': ts})
    return found


def is_notification(r: dict, text: str) -> bool:
    origin = r.get('origin')
    kind = origin.get('kind') if isinstance(origin, dict) else ''
    head = text.lstrip()
    return kind == 'task-notification' or head.startswith(NOTICE_HEADS)


def read_label(path: Path) -> str:
    meta = path.with_suffix('.meta.json')
    if not meta.exists():
        return ''
    data = json.loads(meta.read_text())
    return f'{data.get("agentType", "")}: {data.get("description", "")}'


def take_assistant(t: Transcript, r: dict, n: int, calls: dict[str, Call]) -> None:
    msg = r.get('message')
    content = msg.get('content') if isinstance(msg, dict) else None
    if not isinstance(content, list):
        return
    ts = r.get('timestamp', '')
    for b in content:
        if not isinstance(b, dict):
            continue
        if b.get('type') == 'text':
            add_reply(t, ts, b.get('text', ''))
        elif b.get('type') == 'tool_use':
            name = b.get('name', '')
            inp = b.get('input', {})
            c = Call('claude', t.session, t.agent, ts, name, b.get('id', ''), inp, t.path, n)
            c.cwd = r.get('cwd', '')
            calls[c.id] = c
            t.calls.append(c)
            if c.tool in EDIT_TOOLS and isinstance(inp, dict):
                target = inp.get('file_path') or inp.get('notebook_path')
                if target:
                    t.edited[target] = None


def take_results(t: Transcript, r: dict, results: list[dict], calls: dict[str, Call]) -> None:
    extra = r.get('toolUseResult')
    for b in results:
        c = calls.get(b.get('tool_use_id', ''))
        if c is None:
            continue
        c.output = flatten(b.get('content'))
        c.error = bool(b.get('is_error'))
        saved = SAVED_RE.search(c.output)
        if saved:
            c.saved = saved.group(1)
        if not isinstance(extra, dict):
            continue
        c.task = str(extra.get('agentId') or extra.get('backgroundTaskId') or '')
        if extra.get('status') and not c.status:
            c.status = str(extra['status'])
        diff = extra.get('bashEditDiff')
        for f in diff.get('files', []) if isinstance(diff, dict) else []:
            t.edited[f.get('filePath', '')] = None


def take_user(t: Transcript, r: dict, calls: dict[str, Call], notes: list[dict[str, str]]) -> None:
    msg = r.get('message')
    content = msg.get('content') if isinstance(msg, dict) else None
    ts = r.get('timestamp', '')
    if r.get('isCompactSummary'):
        t.compacts.append(Note(ts, flatten(content)))
        return
    results = []
    if isinstance(content, list):
        results = [b for b in content if isinstance(b, dict) and b.get('type') == 'tool_result']
    if results:
        take_results(t, r, results, calls)
        return
    text = flatten(content)
    if is_notification(r, text):
        notes.extend(parse_notes(text, ts))
    elif not r.get('isMeta'):
        add_prompt(t, ts, clean_prompt(text))


def take_attachment(t: Transcript, r: dict, notes: list[dict[str, str]]) -> None:
    att = r.get('attachment')
    if not isinstance(att, dict) or att.get('type') != 'queued_command':
        return
    text = flatten(att.get('prompt'))
    if att.get('commandMode') == 'task-notification' or is_notification(att, text):
        notes.extend(parse_notes(text, r.get('timestamp', '')))
    elif att.get('commandMode') == 'prompt':
        add_prompt(t, r.get('timestamp', ''), clean_prompt(text), mid=True)


def apply_notes(calls: dict[str, Call], notes: list[dict[str, str]]) -> None:
    by_task = {c.task: c for c in calls.values() if c.task}
    for note in notes:
        c = calls.get(note.get('tool-use-id', '')) or by_task.get(note.get('task-id', ''))
        if c is None:
            continue
        c.status = note.get('status') or c.status
        c.note = note.get('summary') or c.note
        c.task = c.task or note.get('task-id', '')
        if note.get('result'):
            c.output = note['result']


def parse_claude(path: Path, session: str, agent: str) -> Transcript:
    t = Transcript('claude', str(path), session=session, agent=agent)
    if agent:
        t.label = read_label(path)
    calls: dict[str, Call] = {}
    notes: list[dict[str, str]] = []
    for n, r in read_records(path, t):
        ts = r.get('timestamp', '')
        mark_time(t, ts)
        if r.get('cwd'):
            t.cwds.add(r['cwd'])
        if r.get('gitBranch'):
            t.branches.add(r['gitBranch'])
        kind = r.get('type')
        if kind == 'assistant':
            take_assistant(t, r, n, calls)
        elif kind == 'user':
            take_user(t, r, calls, notes)
        elif kind == 'attachment':
            take_attachment(t, r, notes)
        elif kind == 'queue-operation' and r.get('operation') == 'enqueue':
            notes.extend(parse_notes(str(r.get('content') or ''), ts))
        elif kind == 'system' and r.get('subtype') == 'away_summary':
            t.recaps.append(Note(ts, str(r.get('content', ''))))
        elif kind == 'custom-title':
            t.title = r.get('customTitle', '')
        elif kind == 'ai-title':
            t.ai_title = r.get('aiTitle', '')
        elif kind == 'last-prompt':
            t.last_prompt = r.get('lastPrompt', '')
        elif kind == 'pr-link' and r.get('prUrl') not in t.prs:
            t.prs.append(r.get('prUrl', ''))
        elif kind == 'continued-in':
            t.next = r.get('continuedInSessionId', '')
    apply_notes(calls, notes)
    t.notes = notes
    return t


def share_notes(loaded: list[Transcript]) -> None:
    groups: dict[str, list[Transcript]] = {}
    for t in loaded:
        if t.source == 'claude':
            groups.setdefault(t.session, []).append(t)
    for group in groups.values():
        notes = sorted((n for t in group for n in t.notes), key=lambda n: n['ts'])
        for t in group:
            apply_notes({c.id: c for c in t.calls}, notes)


def main_transcript(c: Call) -> Path:
    return Path(c.path).parents[2] / f'{c.session}.jsonl'


def codex_source(meta: dict) -> dict:
    source = meta.get('source')
    if isinstance(source, str) and source.startswith('{'):
        source = json.loads(source)
    if not isinstance(source, dict):
        return {}
    spawn = source.get('subagent', {})
    if not isinstance(spawn, dict):
        return {}
    found = spawn.get('thread_spawn', {})
    return found if isinstance(found, dict) else {}


def shell_text(command: object) -> str:
    if isinstance(command, list):
        argv = [str(x) for x in command]
        if len(argv) >= 3 and argv[1] in ('-lc', '-c'):
            return argv[2]
        return ' '.join(argv)
    return str(command)


def take_item(t: Transcript, item: dict, ts: str, n: int) -> None:
    kind = item.get('type')
    if kind == 'UserMessage':
        add_prompt(t, ts, flatten(item.get('content')).strip())
    elif kind == 'AgentMessage':
        add_reply(t, ts, flatten(item.get('content')))
    elif kind == 'CommandExecution':
        code = item.get('exit_code')
        output = item.get('aggregated_output') or (
            str(item.get('stdout') or '') + str(item.get('stderr') or '')
        )
        command = shell_text(item.get('command'))
        c = Call('codex', t.session, t.agent, ts, kind, item.get('id', ''), command, t.path, n)
        c.cwd = str(item.get('cwd') or '').removeprefix('file://')
        c.output = str(output)
        c.error = code not in (0, None)
        c.status = f'exit {code}'
        t.calls.append(c)
    elif kind == 'FileChange' and isinstance(item.get('changes'), dict):
        for target in item['changes']:
            t.edited[target] = None


def take_response(t: Transcript, p: dict, ts: str, n: int, pending: dict[str, Call]) -> None:
    kind = p.get('type')
    if kind in ('function_call', 'custom_tool_call'):
        inp = p.get('arguments') or p.get('input') or ''
        c = Call(
            'codex', t.session, t.agent, ts, p.get('name', ''), p.get('call_id', ''), inp, t.path, n
        )
        pending[c.id] = c
        t.calls.append(c)
    elif kind in ('function_call_output', 'custom_tool_call_output'):
        c = pending.get(p.get('call_id', ''))
        if c is not None:
            out = p.get('output')
            c.output = out if isinstance(out, str) else flatten(out)


def parse_codex(path: Path) -> Transcript:
    t = Transcript('codex', str(path))
    pending: dict[str, Call] = {}
    for n, r in read_records(path, t):
        ts = r.get('timestamp', '')
        mark_time(t, ts)
        p = r.get('payload')
        if not isinstance(p, dict):
            continue
        kind = r.get('type')
        sub = p.get('type')
        if kind == 'session_meta' and not t.session:
            t.session = p.get('id') or p.get('session_id') or ''
            t.cwds.add(p.get('cwd', ''))
            spawn = codex_source(p)
            t.parent = spawn.get('parent_thread_id', '')
            t.agent = spawn.get('agent_nickname') or spawn.get('agent_path') or ''
            t.label = t.agent
        elif kind == 'compacted' and p.get('message'):
            t.compacts.append(Note(ts, str(p['message'])))
        elif kind == 'response_item':
            take_response(t, p, ts, n, pending)
        elif kind == 'event_msg' and sub == 'item_completed':
            take_item(t, p.get('item') or {}, ts, n)
        elif kind == 'event_msg' and sub == 'user_message':
            add_prompt(t, ts, str(p.get('message', '')).strip())
        elif kind == 'event_msg' and sub == 'agent_message':
            add_reply(t, ts, str(p.get('message', '')))
        elif kind == 'event_msg' and sub == 'task_complete':
            add_reply(t, ts, str(p.get('last_agent_message') or ''))
    if any(c.tool == 'CommandExecution' for c in t.calls):
        t.calls = [c for c in t.calls if c.tool not in CODEX_SHELL_TOOLS]
    home = next(iter(t.cwds), '')
    for c in t.calls:
        c.session = t.session
        c.agent = t.agent
        c.cwd = c.cwd or home
    return t


def claude_files(homes: Homes) -> list[tuple[Path, str, str]]:
    base = homes.claude / 'projects'
    mains = [(p, p.stem, '') for p in base.glob('*/*.jsonl')]
    agents = [
        (p, p.parent.parent.name, p.stem.removeprefix('agent-'))
        for p in base.glob('*/*/subagents/agent-*.jsonl')
    ]
    return mains + agents


def codex_files(homes: Homes) -> list[Path]:
    found = []
    for sub in 'sessions', 'archived_sessions':
        found.extend((homes.codex / sub).rglob('rollout-*.jsonl'))
    return found


def load_all(homes: Homes, roots: list[str] | None) -> list[Transcript]:
    loaded = []
    for path, session, agent in claude_files(homes):
        t = parse_claude(path, session, agent)
        if in_scope(t.cwds, roots):
            loaded.append(t)
    for path in codex_files(homes):
        t = parse_codex(path)
        if in_scope(t.cwds, roots):
            loaded.append(t)
    share_notes(loaded)
    bad = sum(t.bad for t in loaded)
    if bad:
        print(f'skipped {bad} malformed lines', file=sys.stderr)
    return loaded


def by_version(path: Path) -> int:
    digits = path.stem.rsplit('_', 1)[-1]
    return int(digits) if digits.isdigit() else -1


def codex_names(homes: Homes) -> dict[str, str]:
    names: dict[str, str] = {}
    index = homes.codex / 'session_index.jsonl'
    if not index.exists():
        return names
    for r in read_index(index):
        names[r.get('id', '')] = r.get('thread_name', '')
    return names


def codex_goals(homes: Homes) -> dict[str, str]:
    goals: dict[str, str] = {}
    for db in sorted(homes.codex.glob('goals_*.sqlite'), key=by_version):
        con = sqlite3.connect(f'file:{db}?mode=ro', uri=True)
        try:
            rows = con.execute('select thread_id, status, objective from thread_goals').fetchall()
        finally:
            con.close()
        for thread, status, objective in rows:
            goals[thread] = f'{status}: {objective}'
    return goals


def title_of(t: Transcript, names: dict[str, str]) -> str:
    if t.source == 'codex':
        named = names.get(t.session, '')
        first = t.turns[0].prompt if t.turns else ''
        return named or first
    return t.title or t.ai_title or t.last_prompt


def count_hits(t: Transcript, q: Query) -> int:
    units = [searchable(c) for c in t.calls if not is_recall(c)]
    for turn in t.turns:
        units.append(turn.prompt)
        units.extend(turn.replies)
    units.extend(n.text for n in t.compacts + t.recaps)
    return sum(1 for u in units if matches(u, q))


def cmd_sessions(args: argparse.Namespace, homes: Homes) -> int:
    loaded = load_all(homes, args.roots)
    names = codex_names(homes)
    agents: dict[str, list[Transcript]] = {}
    for t in loaded:
        key = t.parent if t.source == 'codex' else t.session
        if t.agent:
            agents.setdefault(key, []).append(t)
    rows = []
    for t in loaded:
        if t.agent:
            continue
        subs = agents.get(t.session, [])
        hits = count_hits(t, args.query)
        sub_hits = sum(count_hits(s, args.query) for s in subs)
        if args.terms and not hits + sub_hits:
            continue
        rows.append((t.last, t, hits, sub_hits, len(subs)))
    rows.sort(key=lambda row: row[0], reverse=True)
    for last, t, hits, sub_hits, n_subs in rows[: args.n]:
        found = f'  hits {hits}+{sub_hits}' if args.terms else ''
        print(
            f'{stamp(last)}  {t.source:6} {t.session}{found}  agents {n_subs}  turns {len(t.turns)}'
        )
        print(f'    {squash(title_of(t, names), 150)}')
        print(f'    {t.path}')
    scanned = sum(1 for t in loaded if not t.agent)
    print(f'{scanned} sessions in scope, {len(rows)} matched, {min(len(rows), args.n)} shown')
    return 0


def find_transcripts(homes: Homes, key: str) -> list[tuple[Path, str]]:
    found = [(p, 'claude') for p, s, a in claude_files(homes) if not a and s.startswith(key)]
    found += [(p, 'codex') for p in codex_files(homes) if p.stem[-36:].startswith(key)]
    return found


def print_text(label: str, text: str, width: int, full: bool) -> None:
    body = text.strip() if full else squash(text, width)
    print(f'  {label} {body}')


def print_turns(t: Transcript, full: bool, tail: int) -> None:
    shown = t.turns[-tail:] if tail else t.turns
    print(f'turns ({len(shown)} of {len(t.turns)}; >> marks a prompt sent mid-turn):')
    for turn in shown:
        print(f'- {stamp(turn.ts)}')
        if turn.prompt:
            print_text('>>' if turn.mid else '>', turn.prompt, 400, full)
        for reply in turn.replies if full else turn.replies[-1:]:
            print_text('<', reply, 800, full)


def print_agents(t: Transcript, homes: Homes) -> None:
    if t.source == 'claude':
        runs = [c for c in t.calls if c.tool in ('Agent', 'Task')]
        print(f'agents ({len(runs)}):')
        for c in runs:
            label = render_input(c.tool, c.inp)
            print(f'  {stamp(c.ts)} {c.id} {c.task} [{c.status or "?"}] {label}')
            text = agent_report(c) or c.note or '(no report recorded)'
            print(f'      {squash(text, 200)}')
        return
    children = [
        child for child in map(parse_codex, codex_files(homes)) if child.parent == t.session
    ]
    print(f'agents ({len(children)}):')
    for child in children:
        final = child.turns[-1].replies[-1:] if child.turns else []
        print(f'  {stamp(child.first)} {child.session} {child.label}')
        print(f'      {squash(final[0] if final else "", 200)}')


def cmd_digest(args: argparse.Namespace, homes: Homes) -> int:
    return print_digest(homes, args.session, args.full, args.tail)


def print_digest(homes: Homes, key: str, full: bool, tail: int) -> int:
    found = find_transcripts(homes, key)
    if len(found) != 1:
        listed = ''.join(f'\n  {p}' for p, _ in found)
        why = 'no session matches' if not found else f'{len(found)} sessions match'
        print(f'Failed: {why} {key}{listed}', file=sys.stderr)
        return 1
    path, source = found[0]
    t = parse_claude(path, path.stem, '') if source == 'claude' else parse_codex(path)
    if t.bad:
        print(f'skipped {t.bad} malformed lines', file=sys.stderr)
    print(f'{t.source} session {t.session}  {stamp(t.first)} .. {stamp(t.last)}')
    print(f'file: {t.path}')
    print(f'title: {squash(title_of(t, codex_names(homes)), 300)}')
    print(f'cwd: {", ".join(sorted(t.cwds))}')
    if t.branches:
        print(f'branches: {", ".join(sorted(t.branches))}')
    if t.source == 'codex':
        goal = codex_goals(homes).get(t.session)
        if goal:
            print(f'goal: {goal}')
        if t.parent:
            print(f'spawned by: {t.parent} as {t.label}')
    for pr in t.prs:
        print(f'pr: {pr}')
    if t.next:
        print(f'continued in: {t.next}')
    for note in t.compacts:
        print(f'compaction summary {stamp(note.ts)}:')
        print(note.text.strip() if full else squash(note.text, 2000))
    for note in t.recaps:
        print(f'recap {stamp(note.ts)}: {note.text.strip()}')
    print_turns(t, full, tail)
    print_agents(t, homes)
    print(f'edited ({len(t.edited)}):')
    for target in t.edited:
        print(f'  {target}')
    return 0


def expand_tools(names: list[str]) -> set[str]:
    wanted: set[str] = set()
    for name in names:
        low = name.lower()
        wanted |= TOOL_GROUPS.get(low, {low})
    return wanted


def rank(c: Call) -> tuple[bool, bool, int]:
    return (bool(c.note), bool(c.status), len(c.output))


def best_calls(calls: list[Call]) -> list[Call]:
    best: dict[tuple[str, str], Call] = {}
    for c in calls:
        key = (c.source, c.id or f'{c.path}:{c.line}')
        held = best.get(key)
        if held is None or rank(c) > rank(held):
            best[key] = c
    return list(best.values())


def call_matches(c: Call, q: Query) -> bool:
    if q.input_only:
        return matches(f'{c.tool}\n{raw_input(c)}', q)
    if matches(searchable(c), q):
        return True
    full = read_saved(c)
    c.deep = bool(full) and matches(f'{searchable(c)}\n{full}', q)
    return c.deep


def select_calls(args: argparse.Namespace, homes: Homes) -> list[Call]:
    tools = expand_tools(args.tool)
    picked = []
    for t in load_all(homes, args.roots):
        for c in t.calls:
            if tools and c.tool.lower() not in tools:
                continue
            if args.since and c.ts < args.since:
                continue
            if args.runs and not is_run(c):
                continue
            if not is_recall(c) and call_matches(c, args.query):
                picked.append(c)
    picked = best_calls(picked)
    picked.sort(key=lambda c: c.ts, reverse=True)
    return picked


def outcome(c: Call) -> str:
    if c.error:
        return f'error {c.status}'.strip()
    return c.status or 'ok'


def preview(c: Call) -> tuple[str, int]:
    body = agent_report(c) if c.tool in ('Agent', 'Task') else c.output
    lines = [x for x in body.splitlines() if x.strip()]
    if not lines:
        return '', 0
    return (lines[0] if c.tool in ('Agent', 'Task') else lines[-1]), len(lines)


def cmd_results(args: argparse.Namespace, homes: Homes) -> int:
    picked = select_calls(args, homes)
    for c in picked[: args.n]:
        who = c.agent or 'main'
        print(f'{stamp(c.ts)}  {c.source} {c.session[:8]} {who}  {c.tool}  {c.id}  [{outcome(c)}]')
        print(f'    in:  {squash(render_input(c.tool, c.inp), 200)}')
        last, count = preview(c)
        print(f'    out: {squash(last, 200)}  ({count} lines)')
        if c.note:
            print(f'    note: {squash(c.note, 200)}')
        if c.deep:
            print(f'    matched in the full output: {c.saved}')
        elif c.saved:
            print(f'    full output: {c.saved}')
    print(f'{len(picked)} calls matched, {min(len(picked), args.n)} shown')
    return 0


def print_body(text: str, limit: int, where: str) -> None:
    if not limit or len(text) <= limit:
        print(text)
        return
    head = limit // 4
    print(text[:head])
    print(f'\n[... {len(text) - limit} chars cut; --max 0 prints all; {where} ...]\n')
    print(text[len(text) - (limit - head) :])


def find_raw(paths: list[Path], key: str) -> list[Path]:
    needle = key.encode()
    found = []
    for p in paths:
        with p.open('rb') as f:
            if any(needle in line for line in f):
                found.append(p)
    return found


def show_agent(homes: Homes, agent: str, limit: int, n: int) -> int:
    hits = list((homes.claude / 'projects').glob(f'*/*/subagents/agent-{agent}.jsonl'))
    if not hits:
        print(f'Failed: no transcript for agent {agent}', file=sys.stderr)
        return 1
    path = hits[0]
    t = parse_claude(path, path.parent.parent.name, agent)
    print(f'agent {agent}  {t.label}  session {t.session}')
    print(f'file: {path}')
    print(f'cwd: {", ".join(sorted(t.cwds))}  {stamp(t.first)} .. {stamp(t.last)}')
    prompt = t.turns[0].prompt if t.turns else ''
    print('\nprompt:')
    print_body(prompt, limit, str(path))
    shown = t.calls[-n:] if n else t.calls
    print(f'\ncalls ({len(shown)} of {len(t.calls)}; -n 0 lists all):')
    for c in shown:
        label = squash(render_input(c.tool, c.inp), 120)
        print(f'  {stamp(c.ts)} {c.tool} {c.id} [{outcome(c)}] {label}')
    final = t.turns[-1].replies[-1] if t.turns and t.turns[-1].replies else ''
    print('\nfinal report:')
    print_body(final, limit, str(path))
    return 0


def git(tree: str, *argv: str) -> subprocess.CompletedProcess:
    return subprocess.run(['git', '-C', tree, *argv], check=False, capture_output=True, text=True)


def tree_of(c: Call) -> tuple[str, str]:
    text = c.inp.get('command', '') if isinstance(c.inp, dict) else str(c.inp)
    for regex, how in (CD_RE, "the command's cd"), (GIT_C_RE, "the command's git -C"):
        m = regex.search(str(text))
        if m is None:
            continue
        path = m.group(1).strip('\'"')
        if '$' in path or '`' in path:
            continue
        path = os.path.expanduser(path)
        if not os.path.isabs(path):
            path = os.path.normpath(os.path.join(c.cwd or '/', path))
        return path, how
    return c.cwd, 'the recorded cwd' if c.source == 'codex' else 'the session cwd'


def describe_tree(c: Call) -> list[str]:
    tree, how = tree_of(c)
    lines = [f'ran in: {tree or "unknown"} (from {how})']
    if not tree:
        return lines
    if not os.path.isdir(tree):
        lines.append(
            'tree is gone: anchor on a SHA printed in the output, else on the branch'
            ' reflog in the main repo (git -C <root> reflog --date=iso <branch>)'
        )
        return lines
    when = f'{c.ts[:19].replace("T", " ")} +0000'
    probe = git(tree, 'rev-parse', '--verify', f'HEAD@{{{when}}}')
    now = git(tree, 'rev-parse', 'HEAD').stdout.strip()
    if probe.returncode != 0:
        lines.append(f'HEAD then: unknown (not a git tree or no reflog); HEAD now: {now or "none"}')
        return lines
    if 'only goes back' in probe.stderr:
        lines.append(f'HEAD then: unknown (the reflog starts after the run); HEAD now: {now}')
        return lines
    then = probe.stdout.strip()
    stat = git(tree, 'diff', '--shortstat', then, 'HEAD').stdout.strip() or 'no committed change'
    dirty = len(git(tree, 'status', '--porcelain').stdout.splitlines())
    lines.append(f'HEAD then: {then} (reflog)  HEAD now: {now}')
    lines.append(f'since then: {stat}; {dirty} paths uncommitted or untracked')
    return lines


def later_reads(c: Call) -> list[Call]:
    t = parse_claude(Path(c.path), c.session, c.agent)
    return [x for x in t.calls if x.ts > c.ts and c.task in searchable(x) and x.id != c.id]


def show_call(c: Call, limit: int) -> None:
    print(f'{c.source} {c.tool} {c.id}  [{outcome(c)}]  {stamp(c.ts)}')
    print(f'session {c.session}  agent {c.agent or "main"}')
    print(f'file: {c.path} line {c.line}')
    for line in describe_tree(c):
        print(line)
    if c.task:
        print(f'task: {c.task}')
    if c.note:
        print(f'notification: {c.note}')
    print('\ninput:')
    raw = c.inp if isinstance(c.inp, str) else json.dumps(c.inp, indent=2, ensure_ascii=False)
    print_body(raw, limit, f'{c.path} line {c.line}')
    print('\noutput:')
    full = read_saved(c)
    if c.saved and not full:
        print(f'[the full output spilled to {c.saved} is gone; only the preview below survives]')
    print_body(full or c.output, limit, c.saved if full else f'{c.path} line {c.line}')
    live = LIVE_RE.search(c.output)
    if live and Path(live.group(1)).is_file():
        print(f'\nbackground output, still on disk at {live.group(1)}:')
        print_body(Path(live.group(1)).read_text(errors='replace'), limit, live.group(1))
    elif live:
        print(f'\n[background output file {live.group(1)} is gone; read the later calls below]')
    if c.source == 'claude' and c.tool == 'Bash' and c.task:
        reads = later_reads(c)
        print(f'\nlater calls naming task {c.task} ({len(reads)}):')
        for x in reads:
            print(f'  {stamp(x.ts)} {x.tool} {x.id} {squash(render_input(x.tool, x.inp), 120)}')


def cmd_show(args: argparse.Namespace, homes: Homes) -> int:
    key = args.id
    if AGENT_ID_RE.fullmatch(key):
        return show_agent(homes, key, args.max, args.n)
    if UUID_RE.fullmatch(key):
        return print_digest(homes, key, full=True, tail=0)
    claude_paths = {p: (s, a) for p, s, a in claude_files(homes)}
    found = []
    for path in find_raw(list(claude_paths), key):
        session, agent = claude_paths[path]
        found += [c for c in parse_claude(path, session, agent).calls if c.id == key]
    if not found:
        for path in find_raw(codex_files(homes), key):
            found += [c for c in parse_codex(path).calls if c.id == key]
    if not found:
        print(f'Failed: no tool call with id {key}', file=sys.stderr)
        return 1
    c = best_calls(found)[0]
    if c.source == 'claude' and c.agent and main_transcript(c).is_file():
        parent = parse_claude(main_transcript(c), c.session, '')
        apply_notes({c.id: c}, parent.notes)
    show_call(c, args.max)
    if len(found) > 1:
        print(f'\n(the same call id is in {len(found) - 1} forked copies of this transcript)')
    if c.tool in ('Agent', 'Task') and AGENT_ID_RE.fullmatch(c.task):
        print(f'\nagent transcript: show {c.task}')
    return 0


def codex_cwds(homes: Homes) -> dict[str, str]:
    cwds = {}
    for path in codex_files(homes):
        with path.open('rb') as f:
            first = f.readline()
        try:
            meta = json.loads(first).get('payload', {})
        except ValueError:
            continue
        cwds[meta.get('id', '')] = meta.get('cwd', '')
    return cwds


def cmd_prompts(args: argparse.Namespace, homes: Homes) -> int:
    rows = []
    claude_sessions = {s for _, s, a in claude_files(homes) if not a}
    history = homes.claude / 'history.jsonl'
    if history.exists():
        for r in read_index(history):
            cwd = r.get('project', '')
            text = r.get('display', '')
            if in_scope({cwd}, args.roots) and matches(text, args.query):
                session = r.get('sessionId', '')
                gone = '' if session in claude_sessions else ' [no transcript]'
                ts = r.get('timestamp', 0) / 1000
                rows.append((ts, 'claude', session, cwd, text, gone))
    history = homes.codex / 'history.jsonl'
    if history.exists():
        cwds = codex_cwds(homes)
        for r in read_index(history):
            session = r.get('session_id', '')
            cwd = cwds.get(session, '')
            text = r.get('text', '')
            if in_scope({cwd}, args.roots) and matches(text, args.query):
                gone = '' if session in cwds else ' [no transcript]'
                rows.append((r.get('ts', 0), 'codex', session, cwd, text, gone))
    rows.sort(key=lambda row: row[0], reverse=True)
    for ts, source, session, cwd, text, gone in rows[: args.n]:
        when = datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M')
        print(f'{when}  {source:6} {session}  {cwd}{gone}')
        print(f'    {squash(text, 200)}')
    print(f'{len(rows)} prompts matched, {min(len(rows), args.n)} shown')
    return 0


def find_roots(path: str) -> list[str]:
    probe = git(path, 'worktree', 'list', '--porcelain')
    if probe.returncode != 0:
        return [path]
    roots = [
        line.removeprefix('worktree ')
        for line in probe.stdout.splitlines()
        if line.startswith('worktree ')
    ]
    return roots or [path]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='recall.py', description='Search Claude Code and Codex session records.'
    )
    parser.add_argument('--claude-dir', default=os.environ.get('CLAUDE_CONFIG_DIR', '~/.claude'))
    parser.add_argument('--codex-dir', default=os.environ.get('CODEX_HOME', '~/.codex'))
    sub = parser.add_subparsers(dest='cmd', required=True)

    def scoped(name: str, text: str) -> argparse.ArgumentParser:
        p = sub.add_parser(name, help=text)
        p.add_argument('-p', '--project', help='any path in the repo (default: the cwd)')
        p.add_argument('-a', '--all', action='store_true', help='every project')
        p.add_argument('-n', type=int, default=20, help='rows to print')
        p.add_argument('--any', action='store_true', help='match ANY term instead of all')
        p.add_argument('-l', '--line', action='store_true', help='all terms on one line')
        p.add_argument('terms', nargs='*', help='quoted terms, any case; -- before a term with -')
        return p

    scoped('sessions', 'sessions newest first, with hit counts')
    results = scoped('results', 'tool calls and agent runs matching terms')
    results.add_argument(
        '-t',
        '--tool',
        action='append',
        default=[],
        help='tool name, repeatable; bash and agent cover Claude and Codex',
    )
    results.add_argument('-I', '--input', action='store_true', help='match the call input only')
    results.add_argument('--since', default='', help='YYYY-MM-DD')
    results.add_argument(
        '-r', '--runs', action='store_true', help='only agents and commands that ran a program'
    )
    scoped('prompts', 'user prompts from the global prompt history')
    digest = sub.add_parser('digest', help='decision trail of one session')
    digest.add_argument('session', help='session id or a unique prefix')
    digest.add_argument('--full', action='store_true', help='no truncation')
    digest.add_argument('--tail', type=int, default=0, help='last N turns only')
    show = sub.add_parser('show', help='full record of one call or agent')
    show.add_argument('id', help='tool call id, agent id or session id')
    show.add_argument('--max', type=int, default=30000, help='chars per body, 0 = all')
    show.add_argument('-n', type=int, default=40, help='agent calls to list, 0 = all')
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    homes = Homes(Path(args.claude_dir).expanduser(), Path(args.codex_dir).expanduser())
    if args.cmd in SCOPED:
        args.terms = [t.lower() for t in args.terms]
        input_only = args.cmd == 'results' and args.input
        args.query = Query(args.terms, any_term=args.any, input_only=input_only, line=args.line)
        project = os.path.abspath(args.project or os.getcwd())
        args.roots = None if args.all else find_roots(project)
    commands = {
        'sessions': cmd_sessions,
        'results': cmd_results,
        'prompts': cmd_prompts,
        'digest': cmd_digest,
        'show': cmd_show,
    }
    return commands[args.cmd](args, homes)


if __name__ == '__main__':
    sys.exit(main())
