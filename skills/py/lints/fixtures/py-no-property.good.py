from typing import Protocol

class Account:
    def balance(self):
        return self._balance


class SocketLike(Protocol):
    @property
    def name(self) -> str: ...
