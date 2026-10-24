class Account:
    @property
    def balance(self):
        return self._balance


class Ledger(Protocol):
    class Account:
        @property
        def balance(self):
            return fetch_balance()
