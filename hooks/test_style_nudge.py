# pyright: basic
import io
import json

import pytest
import style_nudge
from style_nudge import find_miss
from style_nudge import measure
from style_nudge import on_prompt
from style_nudge import on_stop
from style_nudge import on_tool
from style_nudge import visible

SESSION = {'session_id': 'sess', 'cwd': '/repo'}
SHORT = 'Done. The test passes.'
LONG = '\n'.join(f'Line {n} of a reply that runs past the budget.' for n in range(30))


def stop(message, **extra):
    return on_stop({**SESSION, 'last_assistant_message': message, **extra})


def state(fake_kvs):
    return json.loads(fake_kvs.value('caveman', 'sess', '/repo'))


def test_visible_strips_silent_blocks_and_code_fences() -> None:
    message = '<status>working</status>Answer.\n```py\nx = 1\ny = 2\n```\nEnd.'
    assert visible(message) == 'Answer.\n\nEnd.'


def test_measure_counts_rendered_lines_lists_and_bullet_sentences() -> None:
    text = 'x' * 170 + '\n\n- One. Two. Three.\n- Four.\n\n1. a\n2. b\n3. c\n4. d\n5. e\n6. f'
    assert measure(text) == {'lines': 13, 'bullets': 6, 'sentences': 3}


def test_measure_ignores_periods_inside_code() -> None:
    assert measure('- Run `a.b.c` once.')['sentences'] == 1


@pytest.mark.parametrize(
    ('measured', 'cap', 'expected'),
    [
        ({'lines': 27, 'bullets': 0, 'sentences': 0}, 20, {'lines': 27, 'cap': 20}),
        ({'lines': 22, 'bullets': 0, 'sentences': 0}, 25, None),
        ({'lines': 5, 'bullets': 6, 'sentences': 1}, 20, {'bullets': 6, 'cap': 5}),
        ({'lines': 5, 'bullets': 2, 'sentences': 3}, 20, {'sentences': 3, 'cap': 2}),
        ({'lines': 20, 'bullets': 5, 'sentences': 2}, 20, None),
    ],
)
def test_find_miss_names_the_first_broken_rule(measured, cap, expected) -> None:
    assert find_miss(measured, cap) == expected


def test_stop_only_records_a_miss(fake_kvs) -> None:
    assert stop(LONG) is None
    assert state(fake_kvs) == {'level': 1, 'miss': 1, 'ok': 0, 'lines': 30, 'cap': 20}


def test_stop_backs_off_on_a_compliant_reply(fake_kvs) -> None:
    stop(LONG)
    stop(LONG)
    assert state(fake_kvs)['level'] == 2
    stop(SHORT)
    recorded = state(fake_kvs)
    assert recorded['level'] == 1
    assert recorded['ok'] == 1
    assert recorded['lines'] == 30
    stop(SHORT)
    assert state(fake_kvs)['level'] == 0
    stop(SHORT)
    assert state(fake_kvs)['level'] == 0


def test_level_stops_at_three(fake_kvs) -> None:
    for _ in range(5):
        stop(LONG)
    assert state(fake_kvs)['level'] == 3
    assert state(fake_kvs)['miss'] == 5


def test_report_after_tool_work_gets_the_wider_cap(fake_kvs) -> None:
    text = '\n'.join(f'Line {n}.' for n in range(23))
    on_prompt(SESSION)
    for _ in range(4):
        on_tool(SESSION)
    assert stop(text) is None
    assert state(fake_kvs)['level'] == 0
    on_prompt(SESSION)
    stop(text)
    assert state(fake_kvs) == {'level': 1, 'miss': 1, 'ok': 1, 'lines': 23, 'cap': 20}


@pytest.mark.usefixtures('fake_kvs')
def test_prompt_pointer_appears_after_one_miss_and_names_the_measurement() -> None:
    assert on_prompt(SESSION) is None
    stop(LONG)
    assert on_prompt(SESSION) == '<reminder skill="caveman" rule="budget" lines="30" cap="20"/>'


def test_tool_pointer_needs_level_two(fake_kvs) -> None:
    stop(LONG)
    assert on_tool(SESSION) is None
    stop(LONG)
    assert on_tool(SESSION) == '<reminder skill="caveman" rule="budget" lines="30" cap="20"/>'
    assert fake_kvs.value('tools', 'sess', '/repo') == '2'


def test_prompt_resets_the_tool_count(fake_kvs) -> None:
    on_tool(SESSION)
    on_tool(SESSION)
    on_prompt(SESSION)
    assert fake_kvs.value('tools', 'sess', '/repo') == '0'


@pytest.mark.usefixtures('fake_kvs')
def test_revision_request_only_at_level_three_for_a_gross_miss() -> None:
    gross = '\n'.join(f'Line {n}.' for n in range(45))
    assert stop(gross) is None
    assert stop(gross) is None
    assert stop(gross) == (
        '<reminder skill="caveman" rule="budget" lines="45" cap="20">'
        'revise the final answer to the cap; keep the evidence and the uncertainty</reminder>'
    )
    assert stop(LONG) is None


def test_revision_stop_is_not_measured(fake_kvs) -> None:
    assert stop(LONG, stop_hook_active=True) is None
    assert fake_kvs.value('caveman', 'sess', '/repo') is None


def test_empty_or_silent_message_is_not_measured(fake_kvs) -> None:
    assert stop('<status>thinking</status>') is None
    assert on_stop({**SESSION, 'last_assistant_message': None}) is None
    assert fake_kvs.value('caveman', 'sess', '/repo') is None


def run_main(monkeypatch, capsys, payload):
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(payload)))
    style_nudge.main()
    out = capsys.readouterr().out.strip()
    return json.loads(out) if out else None


@pytest.mark.usefixtures('no_kvs')
def test_main_is_silent_without_kvs(monkeypatch, capsys) -> None:
    payload = {**SESSION, 'hook_event_name': 'Stop', 'last_assistant_message': LONG}
    assert run_main(monkeypatch, capsys, payload) is None


@pytest.mark.usefixtures('fake_kvs')
def test_main_emits_the_tool_pointer_as_context(monkeypatch, capsys) -> None:
    stop(LONG)
    stop(LONG)
    out = run_main(monkeypatch, capsys, {**SESSION, 'hook_event_name': 'PostToolUse'})
    assert out == {
        'hookSpecificOutput': {
            'hookEventName': 'PostToolUse',
            'additionalContext': '<reminder skill="caveman" rule="budget" lines="30" cap="20"/>',
        }
    }


def test_main_stop_emits_nothing_on_an_ordinary_miss(fake_kvs, monkeypatch, capsys) -> None:
    payload = {**SESSION, 'hook_event_name': 'Stop', 'last_assistant_message': LONG}
    assert run_main(monkeypatch, capsys, payload) is None
    assert state(fake_kvs)['level'] == 1
