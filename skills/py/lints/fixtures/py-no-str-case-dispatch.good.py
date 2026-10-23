from dataclasses import dataclass
from enum import Enum


@dataclass(frozen=True, slots=True)
class Kline1m:
    open: float
    close: float


@dataclass(frozen=True, slots=True)
class Depth:
    bid: float
    ask: float


class Side(Enum):
    BUY = 'buy'
    SELL = 'sell'


def encode(sample: Kline1m | Depth) -> list[float]:
    match sample:
        case Kline1m():
            return [sample.open, sample.close]
        case Depth():
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
