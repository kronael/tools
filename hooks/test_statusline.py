# pyright: basic
from datetime import datetime
from datetime import timezone

from statusline import render

RESETS = 1738857600
FULL = {
    'model': {'display_name': 'Opus'},
    'context_window': {'used_percentage': 23.9},
    'rate_limits': {
        'five_hour': {'used_percentage': 7.2, 'resets_at': RESETS},
        'seven_day': {'used_percentage': 41.6, 'resets_at': RESETS},
    },
}


def test_weekly_usage_shows_every_whole_percent() -> None:
    """A 41.6% weekly use prints as 41%, with the reset day and time."""
    reset = datetime.fromtimestamp(RESETS, tz=timezone.utc).astimezone().strftime('%a %H:%M')
    assert render(FULL) == f'Opus · ctx 23% · 5h 7% → {reset} · week 41% → {reset}'


def test_low_weekly_usage_still_shows() -> None:
    """A 1% weekly use is shown, not hidden until the limit is near."""
    data = {'rate_limits': {'seven_day': {'used_percentage': 1.0}}}
    assert render(data) == 'week 1%'


def test_missing_rate_limits_leave_the_rest() -> None:
    """Before the first API response, rate_limits is absent: model and context remain."""
    data = {'model': {'display_name': 'Opus'}, 'context_window': {'used_percentage': None}}
    assert render(data) == 'Opus'
