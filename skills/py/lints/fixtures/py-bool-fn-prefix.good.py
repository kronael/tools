import logging
from typing import override


class OnlyErrors(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.ERROR


class Slot:
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Slot)

    def is_valid(self) -> bool:
        return True


def _has_slots(slots: list[Slot]) -> bool:
    return bool(slots)


def test_valid() -> bool:
    return True
