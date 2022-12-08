async def send(obj, batch):
    for args, kwargs in batch:
        yield obj.send(*args, **kwargs)
