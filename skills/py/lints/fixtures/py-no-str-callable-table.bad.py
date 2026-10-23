CHANNELS: dict[str, Callable[[dict[str, object]], list[str]]] = {
    'update/order_book': process_book,
    'update/trade': process_trades,
}

DECODERS: Mapping[str, Callable[[object], Sample]] = {
    'quote/1': decode_quote,
    'book/1': decode_book,
}

HANDLERS: dict[str, Awaitable[None]] = {}
