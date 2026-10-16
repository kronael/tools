# pyright: basic
import json

from lib.reminder import block
from lib.reminder import context
from lib.reminder import emit
from lib.reminder import file
from lib.reminder import reminder
from lib.reminder import skill


def test_skill_is_a_pure_pointer() -> None:
    assert skill('commit') == '<skill name="commit"/>'


def test_file_is_a_pure_pointer() -> None:
    assert file('~/.claude/LOCAL.md') == '<file path="~/.claude/LOCAL.md"/>'


def test_reminder_without_text_is_self_closing() -> None:
    assert (
        reminder('caveman', 'budget', lines=27, cap=20)
        == '<reminder skill="caveman" rule="budget" lines="27" cap="20"/>'
    )


def test_reminder_with_text_and_no_rule() -> None:
    assert (
        reminder('commit', text='uncommitted changes', files=3)
        == '<reminder skill="commit" files="3">uncommitted changes</reminder>'
    )


def test_reminder_escapes_markup() -> None:
    line = reminder('x', text='a < b & "c"', note='"q"')
    assert line == '<reminder skill="x" note=\'"q"\'>a &lt; b &amp; "c"</reminder>'


def test_context_joins_lines_for_the_event() -> None:
    assert context('Stop', 'one', 'two') == {
        'hookSpecificOutput': {'hookEventName': 'Stop', 'additionalContext': 'one\ntwo'},
    }


def test_block_joins_reasons() -> None:
    assert block('a', 'b') == {'decision': 'block', 'reason': 'a\nb'}


def test_emit_prints_json_and_skips_nothing(capsys) -> None:
    emit(None)
    emit(block('x'))
    assert json.loads(capsys.readouterr().out) == {'decision': 'block', 'reason': 'x'}
