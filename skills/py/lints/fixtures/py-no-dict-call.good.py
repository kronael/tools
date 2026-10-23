import logging

log = logging.getLogger(__name__)

FIELDS = {'last_price': 'lastPrice', 'index_price': 'indexPrice'}

empty = {}


def report(message_id: int, pairs: list[tuple[str, int]], base: dict[str, int]) -> None:
    log.info('updating', extra=dict(message_id=message_id))
    log.info(dict(message_id=message_id))
    by_key = dict(pairs)
    merged = dict(base, message_id=message_id)
    copied = dict(**base)
    log.info('%s %s %s', by_key, merged, copied)
