ROOT = Path(__file__).resolve().parents[2]

HERE = os.path.dirname(os.path.abspath(__file__))

FIXTURE = Path(__file__).with_name('fixtures') / 'orders.json'

here = Path(__file__)

TEMPLATES = Path(templates.__file__).parent

data = (Path(__file__).parent / 'orders.json').read_text()

source = Path(Path(__file__).parent / 'worker.py').read_text()

source = Path(load_module(Path(__file__).with_name('worker.py')).__file__).read_text()

ORIGIN = Path(templates.__spec__.origin).parent

HERE_ORIGIN = os.path.dirname(__spec__.origin)

LOCATION = Path(inspect.getfile(worker)).parent

SOURCE_FILE = inspect.getsourcefile(worker)

MODULE_DIR = Path(inspect.getmodule(handler).__file__).parent

DYNAMIC = Path(getattr(templates, '__file__')).parent

DYNAMIC_DQ = os.path.dirname(getattr(templates, "__file__", ""))
