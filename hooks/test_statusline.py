# pyright: basic
from datetime import datetime
from datetime import timezone

from statusline import render

RESETS = 1738857600
FULL = {
    'model': {'display_name': 'Opus 5.5'},
    'context_window': {'used_percentage': 23.9},
    'rate_limits': {
        'five_hour': {'used_percentage': 7.2, 'resets_at': RESETS},
        'seven_day': {'used_percentage': 41.6, 'resets_at': RESETS},
    },
}


def local(fmt: str) -> str:
    return datetime.fromtimestamp(RESETS, tz=timezone.utc).astimezone().strftime(fmt)


def test_the_line_is_model_context_five_hour_and_week() -> None:
    """Every field in a compact line: model initial and version, whole percents, reset times."""
    assert (
        render(FULL)
        == f'O5.5 · c 23% · 5h 7% → {local("%H:%M")} · w 41% → {local("%a %-d. %H:%M")}'
    )


def test_low_weekly_usage_still_shows() -> None:
    """A 1% weekly use is shown, not hidden until the limit is near."""
    data = {'rate_limits': {'seven_day': {'used_percentage': 1.0}}}
    assert render(data) == 'w 1%'


def test_missing_rate_limits_leave_the_rest() -> None:
    """Before the first API response, rate_limits is absent: model and context remain."""
    data = {'model': {'display_name': 'Opus'}, 'context_window': {'used_percentage': None}}
    assert render(data) == 'O'
