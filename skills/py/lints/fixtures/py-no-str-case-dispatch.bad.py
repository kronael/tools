def encode(kind: str, sample: dict[str, float]) -> list[float]:
    match kind:
        case 'quote/1':
            return [sample['o'], sample['c']]
        case 'book/1':
            return [sample['bid'], sample['ask']]
        case _:
            raise ValueError(kind)


def width(kind: str) -> int:
    match kind:
        case 'quote/1' | 'quote_update/1':
            return 6
        case _:
            return 2


def nested(sample: Quote, kind: str) -> int:
    match sample:
        case Quote():
            match kind:
                case 'quote/1':
                    return 6
    return 0


def captured(kind: str) -> int:
    match kind:
        case 'quote/1' as name:
            return len(name)
    return 0


def captured_union(kind: str) -> int:
    match kind:
        case ('quote/1' | 'book/1') as name:
            return len(name)
    return 0


def adjacent(kind: str) -> int:
    match kind:
        case 'quote' '/1' as name:
            return len(name)
    return 0
