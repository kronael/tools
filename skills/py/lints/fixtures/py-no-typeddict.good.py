from dataclasses import dataclass
from upstream import Row

@dataclass(frozen=True)
class Record:
    name: str

def read(row: Row):
    return row['name']

description = 'class Row(TypedDict): pass'
