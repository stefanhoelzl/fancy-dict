def overwrite(old, new):
    return new


def update(old, new):
    old.update(new)
    return old


def extend(old, new):
    old.extend(new)
    return old
