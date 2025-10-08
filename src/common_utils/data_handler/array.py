def chunk_iter(iterable, chunk_size):
    """Yield successive n-sized chunks from iterable."""
    for i in range(0, len(iterable), chunk_size):
        yield iterable[i : i + chunk_size]
