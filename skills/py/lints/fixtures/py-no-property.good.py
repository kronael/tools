from typing import Protocol

class Account:
    def balance(self):
        return self._balance


class Socket(Protocol):
    @property
    def name(self) -> str: ...
