import math
from enum import StrEnum


class ExchangeName(StrEnum):
    HYPERLIQUID_PERP = 'hyperliquid_perp'


def read_base(exchange: ExchangeName, size: int, name: str) -> str:
    if exchange is ExchangeName.HYPERLIQUID_PERP:
        return 'x'
    if exchange is not ExchangeName.HYPERLIQUID_PERP and size == 3:
        return str(math.pi == size)
    return str(name == 'x' or ExchangeName(name) is ExchangeName.HYPERLIQUID_PERP)
