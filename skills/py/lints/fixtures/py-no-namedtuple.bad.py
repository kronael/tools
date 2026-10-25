class Row(NamedTuple):
    name: str

class Row(typing.NamedTuple):
    name: str

Row = typing_extensions.NamedTuple('Row', [('name', str)])

Row = NamedTuple('Row', name=str)
