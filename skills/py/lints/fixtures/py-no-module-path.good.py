import hashlib
import importlib.resources
import os
import pathlib
from pathlib import Path

MIGRATIONS = Path('migrations')
PARENT = os.path.dirname(os.getcwd())
SOURCE_SHA = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
SOURCE_TEXT = pathlib.Path(__file__).read_text(encoding='utf-8')
WORKER_SOURCE = Path(worker.__file__).read_text()


def fixture_dir(pytestconfig):
    return pytestconfig.rootpath / 'tests' / 'assets'


def stub_location(monkeypatch, module):
    monkeypatch.setattr(module, '__file__', 'stub.py')



def packaged_templates():
    return importlib.resources.files('pkg') / 'templates'


DIST = Path('dist')


def probe(module):
    return getattr(module, '__name__')
