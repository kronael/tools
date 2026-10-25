from enum import Enum, Flag


class ChecksumMode(Enum):
    LIVE = 1
    HISTORICAL = 2


class Side(str, Enum):
    BID = 'bid'
    ASK = 'ask'


class Perm(Flag):
    READ = 1
    WRITE = 2


def auto() -> int:
    return 1


value = auto()


class Settings:
    default = auto()
