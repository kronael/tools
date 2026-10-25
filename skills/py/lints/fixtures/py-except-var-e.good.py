def run():
    try:
        risky()
    except ValueError as exc:
        handle(exc)

with epoch() as e:
    use(e)
