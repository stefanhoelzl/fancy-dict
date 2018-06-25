from collections import defaultdict

from fancy_dict import merger
from errors import NoValidMergeStrategyFound
from conditions import always
from query_engine import QueryEngine


class FancyDict(dict):
    @staticmethod
    def default_query_engine():
        return QueryEngine()

    @staticmethod
    def default_condition():
        return always

    @staticmethod
    def default_merge_strategies():
        return [
            merger.MergeStrategy(merger.overwrite),
            merger.MergeStrategy(merger.update, from_types=dict, to_types=dict),
        ]

    @classmethod
    def using_strategies(cls, *strategies, init_with=None):
        fancy_dict = cls(init_with)
        fancy_dict._strategies = list(strategies)
        return fancy_dict

    def __init__(self, __dct=None, **kwargs):
        super().__init__()
        self._strategies = self.default_merge_strategies()
        self._finalized_keys = []
        self._conditions = defaultdict(self.default_condition)
        self.query_engine = self.default_query_engine()
        self.update(__dct)
        self.update(kwargs)

    @property
    def strategies(self):
        return self._strategies

    def derive(self, init_with=None):
        return type(self).using_strategies(*self.strategies,
                                           init_with=init_with)

    def add_strategy(self, strategy):
        self._strategies.append(strategy)

    def add_condition(self, key, condition):
        self._conditions[key] = condition

    def finalize(self, key):
        self._finalized_keys.append(key)

    def __setitem__(self, key, value):
        if key not in self._finalized_keys:
            if isinstance(value, dict):
                value = self.derive(init_with=value)
            super().__setitem__(key, value)

    def query(self, query):
        yield from self.query_engine(query, self)

    def update(self, __dct=None, **kwargs):
        if isinstance(__dct, dict):
            self._update_with_dict(__dct)
        self._update_with_dict(kwargs)

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
            if self._check_condition(dct, k):
                self._update_value(k, v, strategies)

    def _check_condition(self, dct, key):
        if isinstance(dct, FancyDict):
            return dct._conditions[key](self.get(key), dct.get(key))
        return True
