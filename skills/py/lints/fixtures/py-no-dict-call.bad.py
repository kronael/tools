FIELDS = dict(last_price='lastPrice', index_price='indexPrice')

empty = dict()

rows = [dict(a=1), dict(a=2)]

send([dict(a=1)])

schedule(lambda: dict(a=1))


def build():
    return dict(a=1)


def nested():
    return {'outer': dict(a=1)}
