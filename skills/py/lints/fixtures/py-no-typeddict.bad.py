class Row(TypedDict):
    name: str

class Row(typing.TypedDict, total=False):
    name: str

Row = typing_extensions.TypedDict('Row', {'name': str})

Row = TypedDict('Row', name=str)
