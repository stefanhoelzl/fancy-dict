"""A FancyDict is a dict with extended merging and querying functionality."""


from collections import defaultdict

from . import merger
from .errors import NoValidMergeStrategyFound
from .conditions import always
from .query import StringQueryBuilder


class FancyDict(dict):
    """Extends dict by merging strategies and querying functionality.

    Merging strategies can define custom behavior how to merge certain values
    in the dict.

    Conditions can prevent merging a value under certain circumstances.

    Keys can be marked as finalized to avoid futur changes.

    Queries allow it to retrieve values deep inside the dict.
    """
    @staticmethod
    def default_string_query_builder():
        """Default for building a query from a string.

        Can be overriden to customize the behavior.

        Returns:
            type
        """
        return StringQueryBuilder

    @staticmethod
    def default_condition():
        """Default condition to check when a value get updated.

        Can be overriden to customize the behavior.

        Returns:
            always
        """
        return always

    @staticmethod
    def default_merge_strategies():
        """Default merging strategies when updating a value

        Can be overriden to customize the behavior.

        Returns:
            dicts get updated deep and all other types are overwritten.
        """
        return [
            merger.MergeStrategy(merger.overwrite),
            merger.MergeStrategy(merger.update,
                                 from_types=dict, to_types=dict),
        ]

    @classmethod
    def using_strategies(cls, *strategies, init_with=None):
        """Initializes a FancyDict with custom merging strategies

        Args:
            *strategies: list of merging strategies
            init_with: dictionary with initial values

        Returns:
            FancyDict instance
        """
        fancy_dict = cls(init_with)
        fancy_dict.clear_strategies()
        for strategy in strategies:
            fancy_dict.add_strategy(strategy)
        return fancy_dict

    def __init__(self, __dct=None, **kwargs):
        super().__init__()
        self._strategies = self.default_merge_strategies()
        self._finalized_keys = []
        self._conditions = defaultdict(self.default_condition)
        self.update(__dct)
        self.update(kwargs)

    def derive(self, init_with=None):
        """Derives a new FancyDict from the given.

        Merging strategies are transfered to the new FancyDict.
        Merging strageties for a specific key are not transfered.

        Args:
            init_with: initial values for new FancyDict

        Returns:
            FancyDict with same merging strategies
        """
        strategies = (s for s in self.strategies if s.key is None)
        return type(self).using_strategies(*strategies,  init_with=init_with)

    @property
    def strategies(self):
        """Get a list with the active merging strategies

        Returns:
            list of active merging strategies
        """
        return self._strategies

    def add_strategy(self, strategy):
        """Adds a new merging strategy

        Args:
            strategy: merging strategy
        """
        self._strategies.append(strategy)

    def clear_strategies(self):
        """Removes all strategies"""
        self._strategies.clear()

    @property
    def conditions(self):
        """Dictionary to map key to their conditions.

        Returns:
            key to conditions mapping
        """
        return self._conditions

    def set_condition(self, key, condition):
        """Sets the condition to a key

        Args:
            key: key where the condition is applied
            condition: condition so apply
        """
        self._conditions[key] = condition

    def finalize(self, key):
        """Finalizes a key of the dict

        Updates to finalized keys are ignored.

        Args:
            key: key to finalize
        """
        self._finalized_keys.append(key)

    def __setitem__(self, key, value):
        if key not in self._finalized_keys:
            if isinstance(value, dict):
                value = self.derive(init_with=value)
            super().__setitem__(key, value)

    def query(self, query):
        """Runs a query on the FancyDict

        Args:
            query: query to run

        Returns:
            query results
        """
        if isinstance(query, str):
            string_query_builder = self.default_string_query_builder()
            query = string_query_builder(query).build()
        return query.apply(self)

    def update(self, __dct=None, **kwargs):
        """Updates the FancyDict using the given merging strategies."""
        if isinstance(__dct, dict):
            self._update_with_dict(__dct)
        self._update_with_dict(kwargs)

    def _update_value(self, key, new_value, strategies=None):
        strategies = strategies if strategies is not None else self.strategies
        old_value = self.get(key, None)
        for strategy in reversed(strategies):
            if strategy.applies(key, old_value, new_value):
                self[key] = strategy.method(old_value, new_value)
                return
        raise NoValidMergeStrategyFound(key, old_value, new_value)

    def _update_with_dict(self, dct):
        strategies = None
        if isinstance(dct, FancyDict):
            strategies = dct.strategies
        for key, value in dct.items():
            if self._check_condition(dct, key):
                self._update_value(key, value, strategies)

    def _check_condition(self, dct, key):
        if isinstance(dct, FancyDict):
            return dct.conditions[key](self.get(key), dct.get(key))
        return True
