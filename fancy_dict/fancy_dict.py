from fancy_dict import merger


DEFAULT_MERGE_STRATEGIES = (
    merger.MergeStrategy(merger.overwrite),
    merger.MergeStrategy(merger.update, from_types=(dict,), to_types=(dict,)),
)


class FancyDict(dict):
    def __init__(self, __dct=None, **kwargs):
        super().__init__()
        self._strategies = list(DEFAULT_MERGE_STRATEGIES)
        self.update(__dct)
        self.update(kwargs)

    def add_strategy(self, strategy):
        self._strategies.append(strategy)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = FancyDict(value)
        super().__setitem__(key, value)

    def _update_value(self, key, new_value):
        old_value = self.get(key, None)
        for strategy in reversed(self._strategies):
            if strategy.can_merge(key, old_value, new_value):
                self[key] = strategy.method(old_value, new_value)
                return

    def _update_with_dict(self, dct):
        for k, v in dct.items():
            self._update_value(k, v)

    def update(self, __dct=None, **kwargs):
        if isinstance(__dct, dict):
            self._update_with_dict(__dct)
        self._update_with_dict(kwargs)
