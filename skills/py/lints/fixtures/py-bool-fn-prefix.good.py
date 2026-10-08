import logging
import typing
from typing import override


class OnlyErrors(logging.Filter):
    @override
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.ERROR


class OnlyWarnings(logging.Filter):
    @override  # logging.Filter contract
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.WARNING


class OnlyInfo(logging.Filter):
    @typing.override
    def filter(self, record: logging.LogRecord) -> bool:
        return record.levelno >= logging.INFO


class OnlyDebug(logging.Filter):
    @staticmethod
    @override
    def filter(record: logging.LogRecord) -> bool:
        return record.levelno >= logging.DEBUG


class Slot:
    def __eq__(self, other: object) -> bool:
        return isinstance(other, Slot)

    def is_valid(self) -> bool:
        return True


def _has_slots(slots: list[Slot]) -> bool:
    return bool(slots)


def is_slot(x: object) -> typing.TypeGuard[Slot]:
    return isinstance(x, Slot)


def test_valid() -> bool:
    return True


def test() -> bool:
    return True
