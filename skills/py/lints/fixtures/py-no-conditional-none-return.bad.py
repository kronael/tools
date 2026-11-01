async def select_observation(pool: Pool, key: str) -> StoredObservation | None:
    row = await pool.fetchrow(SELECT, key)
    return StoredObservation(**row) if row else None

def tenant(row: Row | None) -> str | None:
    return row.tenant_id if row is not None else None

def parse(value: object) -> bool | None:
    return None if value is None else False

def lower(value: object) -> str | None:
    return (value.lower() if isinstance(value, str) else None)
