def encode(kind: str, sample: dict[str, float]) -> list[float]:
    match kind:
        case 'kline1m/1':
            return [sample['o'], sample['c']]
        case 'depth/1':
            return [sample['bid'], sample['ask']]
        case _:
            raise ValueError(kind)


def width(kind: str) -> int:
    match kind:
        case 'kline1m/1' | 'kline_update/1':
            return 6
        case _:
            return 2
