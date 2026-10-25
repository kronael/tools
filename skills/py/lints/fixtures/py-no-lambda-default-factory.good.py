from dataclasses import dataclass, field


@dataclass
class Bag:
    xs: list = field(default_factory=list)

ys = field(default_factory=dict[str, int])

zs = field(default_factory=lambda: [1])

names = field(default_factory=lambda: {'name': 'item'})

value = field(default_factory=lambda: make_value())

other = choose(factory=lambda: [])

seeded = field(default_factory=lambda seed=make_seed(): [])
