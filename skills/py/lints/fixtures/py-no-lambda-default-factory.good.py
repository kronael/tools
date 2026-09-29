from dataclasses import dataclass, field


@dataclass
class Bag:
    xs: list = field(default_factory=list)
