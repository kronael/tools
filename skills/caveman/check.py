#!/usr/bin/env python3
import json
import math
import re
import statistics
import sys
from dataclasses import dataclass
from dataclasses import field

SKILL = 'caveman'
COLUMNS = 80
CEILING = 20
FENCE = re.compile(r'^[ \t]*((`|~)\2{2,})(?!\2)[\s\S]*?^[ \t]*\1\2*[ \t]*$', re.MULTILINE)
LINK = re.compile(r'\[([^\]]*)\]\([^)]*\)')


def rendered_lines(reply):
    text = LINK.sub(r'\1', FENCE.sub('', reply)).strip()
    return sum(
        1 if not line.strip() else math.ceil(len(line) / COLUMNS) for line in text.split('\n')
    )


@dataclass
class Window:
    prompts: int = 0
    pointed_prompts: int = 0
    is_loaded: bool = False
    unloaded_replies: int = 0
    reply_lines: list[int] = field(default_factory=list)
    draft: str = ''

    def close_reply(self):
        if not self.draft:
            return
        self.reply_lines.append(rendered_lines(self.draft))
        if not self.is_loaded:
            self.unloaded_replies += 1
        self.draft = ''

    def add_prompt(self, text):
        self.close_reply()
        self.prompts += 1
        self.is_loaded = self.is_loaded or f'<command-name>/{SKILL}</command-name>' in text

    def add_attachment(self, attachment):
        kind = attachment.get('type')
        if kind == 'invoked_skills':
            names = [skill.get('name') for skill in attachment.get('skills', [])]
            self.is_loaded = self.is_loaded or SKILL in names
        is_prompt_hook = (
            kind == 'hook_additional_context' and attachment.get('hookEvent') == 'UserPromptSubmit'
        )
        if is_prompt_hook and f'{SKILL} skill' in '\n'.join(attachment.get('content', [])):
            self.pointed_prompts += 1

    def add_assistant_block(self, block):
        if block.get('type') == 'text' and block.get('text', '').strip():
            self.draft = block['text']
        if block.get('type') == 'tool_use' and block.get('name') == 'Skill':
            self.is_loaded = self.is_loaded or block.get('input', {}).get('skill') == SKILL

    def report(self, number):
        loaded = 'yes' if self.is_loaded else 'NO'
        over = [n for n in self.reply_lines if n > CEILING]
        median = statistics.median(self.reply_lines)
        return (
            f'window {number}: skill loaded {loaded}; '
            f'replies before the load {self.unloaded_replies} of {len(self.reply_lines)}; '
            f'hook line on {self.pointed_prompts} of {self.prompts} prompts; '
            f'over {CEILING} lines {len(over)} of {len(self.reply_lines)} '
            f'(median {median:g}, max {max(self.reply_lines)})'
        )


def is_prompt(record):
    content = record.get('message', {}).get('content')
    if record.get('isMeta') or record.get('isCompactSummary'):
        return False
    if isinstance(content, str):
        return True
    return not any(block.get('type') == 'tool_result' for block in content or [])


def prompt_text(record):
    content = record['message']['content']
    if isinstance(content, str):
        return content
    return '\n'.join(block.get('text', '') for block in content)


def read_windows(lines):
    windows = [Window()]
    for line in lines:
        try:
            record = json.loads(line)
        except ValueError:
            continue
        if record.get('isSidechain'):
            continue
        kind = record.get('type')
        if kind == 'system' and record.get('subtype') == 'compact_boundary':
            windows[-1].close_reply()
            windows.append(Window())
        elif kind == 'attachment':
            windows[-1].add_attachment(record.get('attachment', {}))
        elif kind == 'user' and is_prompt(record):
            windows[-1].add_prompt(prompt_text(record))
        elif kind == 'assistant':
            for block in record.get('message', {}).get('content') or []:
                windows[-1].add_assistant_block(block)
    windows[-1].close_reply()
    return [window for window in windows if window.reply_lines]


def main():
    if len(sys.argv) != 2:
        sys.exit('Usage: check.py <transcript.jsonl>')
    with open(sys.argv[1], errors='replace') as f:
        windows = read_windows(f)
    for number, window in enumerate(windows, 1):
        print(window.report(number))
    sys.exit(1 if any(window.unloaded_replies for window in windows) else 0)


if __name__ == '__main__':
    main()
