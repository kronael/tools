async def select_observation(pool: Pool, key: str) -> StoredObservation | None:
    row = await pool.fetchrow(SELECT, key)
    if not row:
        return None
    return StoredObservation(**row)

def sign(x: float) -> int:
    return 1 if x >= 0 else -1

def first(rows: list[Row]) -> Row | None:
    return next(iter(rows), None)

def label(row: Row | None) -> str:
    return describe(None) if row is None else describe(row)
