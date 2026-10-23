class Account:
    @property
    def balance(self):
        return self._balance


class AccountLike(Protocol):
    class Account:
        @property
        def balance(self):
            return fetch_balance()
