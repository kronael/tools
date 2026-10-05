#!/usr/bin/env python3
import json
import os
import re
import sys

from lib.state import session_state

STYLE_RULES = """Output style — caveman, in full at ~/.claude/output-styles/caveman.md:
- Lead with the answer. No preamble, no recap of what the diff already shows.
- ~17 lines, hard max 20. No tables or headers in a normal reply.
- Plain words, active voice, one instruction per sentence (ASD-STE100).
- Last line carries the next action, or the bottom line.
- Before sending: read ONLY your first and last line. If those two do not
  say what to DO and what HAPPENED, the middle is padding."""

DOCS_RULES = """Documentation naming rules (layout: the readme skill's topology.md):
- Organized in directories: use lowercase (specs/multi-tenancy.md, docs/setup.md); NO todos/ dir; plans/ only as .claude/plans/ (plan mode's directory, where ship records live)
- NEVER use lowercase for root documentation files (todo.md, readme.md)"""

COMMIT_RULES = """Commit rules:
- Format: "type(scope): Message" (scope optional), subject <= 72 chars (overflow -> second -m body)
- ALWAYS commit in detached HEAD - NEVER on or creating a branch
- NEVER git add -A, NEVER git commit -a, NEVER amend, NEVER push, NEVER squash
- NEVER skip pre-commit hooks
- Pre-commit reformats on first run - ALWAYS retry commit once
Invoke /commit skill."""

SOLVE_NUDGE = (
    'New task (first prompt this session): run /solve before acting — it '
    'loads diary + memory context and routes to the right skill. Skip only '
    'if this prompt is a direct continuation of work already in context.'
)

AGENT_KEYWORDS = {
    'architecture': '/specs',
    'background': '/dispatch',
    'bugs': '/bugs',
    'ceo': '/ceo-eval',
    'cont': '/continue',
    'continue': '/continue',
    'create': '/create',
    'cto': '/cto-eval',
    'design': '/specs',
    'diagram': '/diagrams',
    'diary': '/diary',
    'dispatch': '/dispatch',
    'draft': '/pr-draft',
    'eval': '/create-eval',
    'explore': '/explore',
    'fin': '/fin',
    'fix': '/fix',
    'flowchart': '/diagrams',
    'humanize': '/humanize',
    'inline': '/gh-comment',
    'merge': '/merge',
    'microcopy': '/writing',
    'novice': '/13yo-eval',
    'pentest': '/red-eval',
    'recall': '/recall-memories',
    'refine': '/refine',
    'release': '/release',
    'roi': '/ceo-eval',
    'scavenge': '/scavenge',
    'security': '/red-eval',
    'ship': '/ship',
    'sonnet': '/sonnet',
    'spec': '/specs',
    'specs': '/specs',
    'test': '/software',
    'testing': '/software',
    'thread': '/tweet',
    'tooltip': '/writing',
    'tweet': '/tweet',
    'ux': '/13yo-eval',
    'usability': '/13yo-eval',
    'walkthrough': '/13yo-eval',
    'wisdom': '/wisdom',
    'writing': '/writing',
    'readme': '@readme',
    'learn': '@learn',
    'improve': '@improve',
    'visual': '@visual',
    'distill': '@distill',
    'review': '/review',
    'browse': '/browse',
}

CODEX_PATTERNS = [
    r'\bask\s+(?:codex|astra)\b',
    r'\boracle\b',
    r'\bsecond\s+opinion\b',
]

ESCALATION_PATTERNS = [
    (r'(?<!\S)/(fable|opus)\b', {'fable': '/fable', 'opus': '/opus'}),
    (
        r'\b(?:use|spawn|run|invoke|switch to)\s+(fable|opus)\b',
        {'fable': '/fable', 'opus': '/opus'},
    ),
]


def exact_match(word, keywords):
    word = word.lower()
    if word in keywords:
        return keywords[word]
    if word.endswith('s') and word[:-1] in keywords:
        return keywords[word[:-1]]
    if word + 's' in keywords:
        return keywords[word + 's']
    return None


META_PATTERNS = [
    r'\bhook\b',
    r'\bagent\b.*\b(check|fix|issue)',
    r'\b(check|fix|debug)\b.*(hook|agent|nudge|settings)',
    r'invoke.*agent',
]


# Claude Code spellings only. codex_hook.py rewrites `/name` to Codex's
# `@name`, and a spelling written here instead never reaches that rewriter.
def explicit_route(prompt, harness=None):
    lower = prompt.lower()
    if harness != 'codex':
        # A leading slash command only: "use sol" is as likely the Solana token
        # as the skill, and "/sol/data" a path.
        match = re.match(r'\s*/(astra|sol)(?![\w/.-])', lower)
        if match:
            return '/' + match.group(1)
        for pattern in CODEX_PATTERNS:
            if re.search(pattern, lower):
                return '/astra'
    for pattern, routes in ESCALATION_PATTERNS:
        match = re.search(pattern, lower)
        if match:
            return routes.get(match.group(1))
    words = re.findall(r'\b[a-zA-Z]{2,}\b', prompt)
    for word in words:
        matched = exact_match(word, AGENT_KEYWORDS)
        if matched:
            return matched
    return None


def first_prompt_of_session(session_id):
    """True the first time a session submits a prompt, recording a marker so
    later prompts stay silent. False when the marker exists or cannot be
    written, so an unwritable state dir never turns the nudge into per-prompt
    spam."""
    marker = session_state('solve-nudge', session_id)
    if marker is None or os.path.exists(marker):
        return False
    try:
        open(marker, 'w').close()
    except OSError:
        return False
    return True


def emit(text):
    # additionalContext is the only UserPromptSubmit field the model reads;
    # systemMessage renders in the transcript for the user and never reaches
    # the model.
    print(
        json.dumps(
            {
                'hookSpecificOutput': {
                    'hookEventName': 'UserPromptSubmit',
                    'additionalContext': text,
                },
            }
        )
    )


def main():
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError, ValueError):
        sys.exit(0)

    if not isinstance(data, dict):
        sys.exit(0)

    prompt = data.get('prompt') or ''
    if not isinstance(prompt, str):
        sys.exit(0)

    if any(re.search(p, prompt, re.IGNORECASE) for p in META_PATTERNS):
        emit(STYLE_RULES)
        sys.exit(0)

    parts = []

    if (
        prompt.strip()
        and first_prompt_of_session(data.get('session_id'))
        and not re.search(r'/solve\b', prompt)
    ):
        parts.append(SOLVE_NUDGE)

    # Every turn. The style is in the system prompt and dilutes there; this is
    # the copy that arrives next to the user's message.
    parts.append(STYLE_RULES)

    if re.search(r'\b(todo|readme|changelog|spec|architecture)\b|\.md\b', prompt, re.IGNORECASE):
        parts.append(DOCS_RULES)

    matched = explicit_route(prompt, data.get('harness'))

    if re.search(r'\bcommit\b', prompt, re.IGNORECASE):
        parts.append(COMMIT_RULES)
    elif matched:
        parts.append(f'info: Invoke {matched}.')

    emit('\n\n'.join(parts))

    sys.exit(0)


if __name__ == '__main__':
    main()
