from pydantic import TypeAdapter
import pydantic

FRAME = TypeAdapter(Frame)
FRAMES = pydantic.TypeAdapter(list[Frame])

class Venue:
    ADAPTER = TypeAdapter(Frame)

def decode(raw: bytes) -> Frame:
    return FRAME.validate_json(raw)

def describe() -> str:
    return 'TypeAdapter(Frame) is built once'
