from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Quote:
    open: float
    close: float


@dataclass(frozen=True, slots=True)
class Book:
    bid: float
    ask: float


def encode(sample: Quote | Book) -> list[float]:
    match sample:
        case Quote():
            return [sample.open, sample.close]
        case Book():
            return [sample.bid, sample.ask]


LIMITS: dict[str, int] = {'quote': 6, 'book': 2}

NAMES: Mapping[str, str] = {'quote': 'Quote'}

PENDING: dict[str, Awaitable[None]] = {}

JOBS: dict[str, Coroutine[None, None, int]] = {}
