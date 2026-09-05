import io
import json

import pytest
from prompt_nudge import explicit_route
from prompt_nudge import main


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
