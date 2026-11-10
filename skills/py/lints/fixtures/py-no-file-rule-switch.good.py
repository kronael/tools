# pyright: basic
import sys

print(sys.argv)  # noqa: T201
value = sys._getframe()  # pyright: ignore[reportPrivateUsage]
