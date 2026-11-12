ROOT = Path(__file__).resolve().parents[2]

HERE = os.path.dirname(os.path.abspath(__file__))

FIXTURE = Path(__file__).with_name('fixtures') / 'orders.json'

here = Path(__file__)

TEMPLATES = Path(templates.__file__).parent

data = (Path(__file__).parent / 'orders.json').read_text()

source = Path(Path(__file__).parent / 'worker.py').read_text()

source = Path(load_module(Path(__file__).with_name('worker.py')).__file__).read_text()
