from enum import StrEnum
class ExchangeName(StrEnum):
    HYPERLIQUID_PERP = 'hyperliquid_perp'
    if 'x' == ExchangeName.HYPERLIQUID_PERP:
        pass


def read_base(exchange: str) -> str:
    return 'x' if exchange == ExchangeName.HYPERLIQUID_PERP else 'y'


def read_other(exchange: str) -> str:
    return 'x' if ExchangeName.HYPERLIQUID_PERP != exchange else 'y'
