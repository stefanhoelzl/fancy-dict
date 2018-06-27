"""A FancyDict is a dict with extended merging and querying functionality."""


from collections import defaultdict

from . import merger
from .errors import NoValidMergeStrategyFound
from .conditions import always
from .query import StringQueryBuilder


class Annotation:
    """Annotation for a FancyDict key

    Composed of a merge strategy, a merge condition and if the key is finalized
    """

    def __init__(self, merge_method=None, condition=None, finalize=False):
        self.merge_method = merge_method
        self.condition = condition
        self.finalize = finalize


class FancyDict(dict):
    """Extends dict by merging strategies and querying functionality.

    Merging strategies can define custom behavior how to merge certain values
    in the dict.

    Conditions can prevent merging a value under certain circumstances.

    Keys can be marked as finalized to avoid futur changes.

    Queries allow it to retrieve values deep inside the dict.
    """
    DEFAULT_STRING_QUERY_BUILDER = StringQueryBuilder

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

    def __init__(self, __dct=None, **kwargs):
        super().__init__()
        self._strategies = self.default_merge_strategies()
        self._finalized = {}
        self._conditions = defaultdict(self.default_condition)
        init_values = __dct if __dct else {}
        init_values.update(kwargs)
        if isinstance(init_values, FancyDict):
            self.update(init_values)
        else:
            self.init_with_values(**init_values)

    def init_with_values(self, **init_values):
        for k, v in init_values.items():
            self[k] = v

    def annotate(self, key, annotation):
        if annotation.condition:
            self._conditions[key] = annotation.condition
        self._finalized[key] = annotation.finalize
        if annotation.merge_method:
            self._strategies.append(
                merger.MergeStrategy(key=key, method=annotation.merge_method)
            )

    def __setitem__(self, key, value):
        if not self._finalized.get(key, False):
            if isinstance(value, dict):
                value = type(self)(value)
            super().__setitem__(key, value)

    def query(self, query):
        """Runs a query on the FancyDict

        Args:
            query: query to run

        Returns:
            query results
        """
        if isinstance(query, str):
            query = self.DEFAULT_STRING_QUERY_BUILDER(query).build()
        return query.apply(self)

    def update(self, __dct=None, **kwargs):
        """Updates the FancyDict using the given merging strategies."""
        if isinstance(__dct, dict):
            self._update_with_dict(__dct)
        self._update_with_dict(kwargs)

    def _update_with_dict(self, dct):
        if isinstance(dct, FancyDict):
            fancy_dict = dct
        else:
            fancy_dict = type(self)(dct)
        fancy_dict.merge_into(self)

    def merge_into(self, other_dict):
        for key, new_value in self.items():
            old_value = other_dict.get(key)
            if self._conditions[key](old_value, new_value):
                for strategy in reversed(self._strategies):
                    if strategy.applies(key, old_value, new_value):
                        other_dict[key] = strategy(old_value, new_value)
                        break
                else:
                    raise NoValidMergeStrategyFound(key, old_value, new_value)
