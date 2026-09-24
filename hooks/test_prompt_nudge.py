import io
import json

import prompt_nudge
import pytest
from prompt_nudge import explicit_route
from prompt_nudge import main


@pytest.fixture(autouse=True)
def state_root(tmp_path, monkeypatch):
    monkeypatch.setenv('KRONAEL_HOOK_STATE', str(tmp_path / 'state'))


def run(monkeypatch, capsys, prompt, session_id='sess'):
    data = {'prompt': prompt, 'session_id': session_id, 'cwd': '.'}
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(data)))
    with pytest.raises(SystemExit):
        main()
    out = capsys.readouterr().out.strip()
    return json.loads(out)['hookSpecificOutput']['additionalContext'] if out else ''


def test_code_does_not_route_to_codex() -> None:
    assert explicit_route('write code for this') is None


def test_codex_route_requires_explicit_second_opinion() -> None:
    assert explicit_route('ask codex for a second opinion') == '/codex'
    assert explicit_route('oracle this') == '/codex'


def test_codex_route_suppressed_inside_codex() -> None:
    # The harness comes from the payload codex_hook.py writes, never from the
    # environment: an env var is inherited, and a Claude Code session started
    # from inside Codex would read it and route as if it were Codex.
    assert explicit_route('ask codex for a second opinion', harness='codex') is None


def test_route_is_always_a_claude_code_spelling() -> None:
    # codex_hook.py rewrites `/name` to `@name`. A second spelling written here
    # would never reach that rewriter.
    assert explicit_route('use fable for this', harness='codex') == '/fable'


def test_fable_requires_explicit_escalation() -> None:
    assert explicit_route('fable nudge is bad') is None
    assert explicit_route('use fable for this') == '/fable'
    assert explicit_route('/fable handle this') == '/fable'


def test_continue_routes_to_continue_skill() -> None:
    assert explicit_route('continue') == '/continue'
    assert explicit_route('cont') == '/continue'
    assert explicit_route('pick up where we left off') is None


def test_ship_phrasings_route_to_ship() -> None:
    for prompt in ('ship this', 'ship it', "let's ship", 'and ship it'):
        assert explicit_route(prompt) == '/ship', prompt


def test_output_reaches_the_model(monkeypatch, capsys) -> None:
    # Only hookSpecificOutput.additionalContext is added to the model's context;
    # systemMessage is rendered for the user alone.
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps({'prompt': 'ship it'})))
    with pytest.raises(SystemExit):
        main()
    out = json.loads(capsys.readouterr().out)
    assert 'systemMessage' not in out
    assert out['hookSpecificOutput']['hookEventName'] == 'UserPromptSubmit'
    assert 'info: Invoke /ship.' in out['hookSpecificOutput']['additionalContext']


def test_first_prompt_nudges_solve(monkeypatch, capsys) -> None:
    assert prompt_nudge.SOLVE_NUDGE in run(monkeypatch, capsys, 'add a health endpoint')


def test_continuation_does_not_nudge_solve(monkeypatch, capsys) -> None:
    run(monkeypatch, capsys, 'add a health endpoint')
    assert prompt_nudge.SOLVE_NUDGE not in run(monkeypatch, capsys, 'now wire it into main')


def test_solve_nudge_precedes_route_on_first_prompt(monkeypatch, capsys) -> None:
    text = run(monkeypatch, capsys, 'ship this feature')
    assert text.startswith(prompt_nudge.SOLVE_NUDGE)
    assert '/ship' in text


def test_explicit_solve_prompt_is_not_nudged(monkeypatch, capsys) -> None:
    # User already invoked /solve: no nudge, and first-prompt status is still
    # consumed so the next prompt is a silent continuation.
    assert prompt_nudge.SOLVE_NUDGE not in run(monkeypatch, capsys, '/solve this request')
    assert prompt_nudge.SOLVE_NUDGE not in run(monkeypatch, capsys, 'now do the work')


def test_empty_prompt_is_not_consumed(monkeypatch, capsys) -> None:
    # A whitespace payload is not a task: no nudge, and it does not burn the
    # session's first-prompt status.
    assert prompt_nudge.SOLVE_NUDGE not in run(monkeypatch, capsys, '   ')
    assert prompt_nudge.SOLVE_NUDGE in run(monkeypatch, capsys, 'add a feature')


def test_meta_first_prompt_is_transparent(monkeypatch, capsys) -> None:
    # A hook-debugging prompt is skipped without consuming first-prompt status;
    # the next real prompt still gets the solve nudge.
    assert prompt_nudge.SOLVE_NUDGE not in run(monkeypatch, capsys, 'debug the hook')
    assert prompt_nudge.SOLVE_NUDGE in run(monkeypatch, capsys, 'add a feature')


def test_nudge_is_keyed_by_session_not_cwd(monkeypatch, capsys) -> None:
    run(monkeypatch, capsys, 'add a feature', session_id='a')
    assert prompt_nudge.SOLVE_NUDGE in run(monkeypatch, capsys, 'add a feature', session_id='b')
