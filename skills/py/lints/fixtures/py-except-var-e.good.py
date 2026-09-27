def run():
    try:
        risky()
    except ValueError as exc:
        handle(exc)
