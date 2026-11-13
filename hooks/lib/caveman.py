import json
import os


def caveman_selected(home):
    try:
        with open(os.path.join(home, '.claude', 'settings.json')) as f:
            return json.load(f).get('outputStyle') == 'caveman'
    except (OSError, ValueError, AttributeError):
        return False
