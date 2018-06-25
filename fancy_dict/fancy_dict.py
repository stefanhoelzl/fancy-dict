from fancy_dict import merger
from errors import NoValidMergeStrategyFound


class FancyDict(dict):
    @staticmethod
    def default_merge_strategies():
        return [
            merger.MergeStrategy(merger.overwrite),
            merger.MergeStrategy(merger.update,
                                 from_types=(dict,), to_types=(dict,)),
        ]

    @classmethod
    def using_strategies(cls, *strategies, init_with=None):
        fancy_dict = cls(init_with)
        fancy_dict._strategies = list(strategies)
        return fancy_dict

    @classmethod
    def derive_from(cls, base, init_with=None):
        fancy_dict = cls(init_with)
        fancy_dict._strategies = base.strategies
        return fancy_dict

    def __init__(self, __dct=None, **kwargs):
        super().__init__()
        self._strategies = self.default_merge_strategies()
        self.update(__dct)
        self.update(kwargs)

    @property
    def strategies(self):
        return self._strategies

    def add_strategy(self, strategy):
        self._strategies.append(strategy)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = type(self).derive_from(self, init_with=value)
        super().__setitem__(key, value)

    def _update_value(self, key, new_value, strategies=None):
        strategies = strategies if strategies is not None else self.strategies
        old_value = self.get(key, None)
        for strategy in reversed(strategies):
            if strategy.can_merge(key, old_value, new_value):
                self[key] = strategy.method(old_value, new_value)
                return
        raise NoValidMergeStrategyFound(key, old_value, new_value)

    def _update_with_dict(self, dct):
        strategies = None
        if isinstance(dct, FancyDict):
            strategies = dct.strategies
        for k, v in dct.items():
            self._update_value(k, v, strategies)

    def update(self, __dct=None, **kwargs):
        if isinstance(__dct, dict):
            self._update_with_dict(__dct)
        self._update_with_dict(kwargs)
