def valid(slot: int) -> bool:
    return slot > 0

async def alive() -> bool:
    return True

def quoted() -> 'bool':
    return True

def double_quoted() -> "bool":
    return True

def numeric(x: object) -> TypeGuard[int]:
    return isinstance(x, int)

def narrowed(x: object) -> typing.TypeIs[int]:
    return isinstance(x, int)

def testing_mode() -> bool:
    return True

def tested() -> bool:
    return True

def _private() -> bool:
    return True

class Slot:
    @no_override
    def check(self) -> bool:
        return True

@override
class Base:
    def check(self) -> bool:
        return True
