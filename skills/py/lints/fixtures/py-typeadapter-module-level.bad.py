def decode(raw: bytes) -> Frame:
    return TypeAdapter(Frame).validate_json(raw)

def decode_int():
    return TypeAdapter[int](int)

async def read(raw: dict) -> list[Frame]:
    return pydantic.TypeAdapter(list[Frame]).validate_python(raw)

class Venue:
    def parse(self, raw: bytes) -> Frame:
        adapter = TypeAdapter(Frame)
        return adapter.validate_json(raw)
