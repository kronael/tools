def run():
    try:
        risky()
    except ValueError as e:
        handle(e)
