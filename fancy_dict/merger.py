class MergeStrategy:
    def __init__(self, method, key=None, from_types=None, to_types=None):
        self.method = method
        self.key = key
        self.from_types = from_types
        self.to_types = to_types

    def can_merge(self, key, old, new):
        if self.key is None or self.key == key:
            if self.from_types is None or isinstance(old, self.from_types):
                if self.to_types is None or isinstance(new, self.to_types):
                    return True
        return False


def overwrite(old, new):
    return new


def update(old, new):
    old.update(new)
    return old


def add(old, new):
    return old + new
