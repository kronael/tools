"""One XML shape for every line a hook adds to the model's context.

A pure pointer names a skill or a file. A reminder names the skill, the rule
it points at and the measured values; text is optional and one line.
Nothing else is ever injected.
"""

import json
from xml.sax.saxutils import escape
from xml.sax.saxutils import quoteattr


def skill(name):
    return f'<skill name={quoteattr(name)}/>'


def file(path):
    return f'<file path={quoteattr(path)}/>'


def reminder(skill_name, rule=None, text=None, **measured):
    attrs = [f'skill={quoteattr(skill_name)}']
    if rule:
        attrs.append(f'rule={quoteattr(rule)}')
    attrs.extend(f'{key}={quoteattr(str(value))}' for key, value in measured.items())
    head = ' '.join(attrs)
    if not text:
        return f'<reminder {head}/>'
    return f'<reminder {head}>{escape(text)}</reminder>'


def context(event, *lines):
    """additionalContext for the lifecycle events that feed it to the model."""
    return {
        'hookSpecificOutput': {
            'hookEventName': event,
            'additionalContext': '\n'.join(lines),
        },
    }


def block(*lines):
    """A Stop decision that makes the model continue with the reason."""
    return {'decision': 'block', 'reason': '\n'.join(lines)}


def emit(output):
    if output:
        print(json.dumps(output))
