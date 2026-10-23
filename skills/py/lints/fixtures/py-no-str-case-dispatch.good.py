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
