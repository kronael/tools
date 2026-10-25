from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class Quote:
    open: float
    close: float


@dataclass(frozen=True, slots=True)
class Book:
    bid: float
    ask: float


class Side(Enum):
    BUY = 'buy'
    SELL = 'sell'


def encode(sample: Quote | Book) -> list[float]:
    match sample:
        case Quote():
            return [sample.open, sample.close]
        case Book():
            return [sample.bid, sample.ask]


def sign(side: Side) -> int:
    match side:
        case Side.BUY:
            return 1
        case Side.SELL:
            return -1


def first(values: list[int]) -> int:
    match values:
        case [head, *_]:
            return head
        case _:
            return 0


def captured(sample: Quote | Book | Side) -> int:
    match sample:
        case Quote() as quote:
            return int(quote.open)
        case Side.BUY as side:
            return 1
    return 0


def captured_payload(payload) -> int:
    match payload:
        case {'kind': 'quote/1'} as record:
            return len(record)
        case ['book/1', count] as values:
            return len(values)
        case ('quote/1', count) as values:
            return len(values)
        case ('book/1',) as values:
            return len(values)
    return 0
