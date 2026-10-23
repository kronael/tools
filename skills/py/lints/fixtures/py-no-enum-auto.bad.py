from enum import Enum, auto
class ChecksumMode(Enum):
    LIVE = auto()
    HISTORICAL = auto()

import enum
class Phase(enum.Enum):
    RAMP_UP = enum.auto()
