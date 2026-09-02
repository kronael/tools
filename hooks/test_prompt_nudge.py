from prompt_nudge import explicit_route


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
