"""A FancyDict is a dict with extended merging and querying functionality."""

from . import merger
from .errors import NoValidMergeStrategyFound
from .conditions import always
from .query import StringQueryBuilder


class Annotations:
    """Annotations for a FancyDict key

    Composed of a merge strategy, a merge condition and if the key is finalizedd
    """
    DEFAULTS = {
        "merge_method": merger.overwrite,
        "condition": always,
        "finalized": False
    }

    def __init__(self, **kwargs):
        self._values = kwargs

    def get(self, key):
        return self._values.get(key)

    def __getattr__(self, item):
        if item in self.DEFAULTS:
            default = self.DEFAULTS[item]
            return self._values[item] if item in self._values else default
        return super().__getattribute__(item)

    def update(self, annotations):
        for key in self.DEFAULTS:
            if annotations.get(key) is not None:
                self._values[key] = getattr(annotations, key)


class FancyDict(dict):
    """Extends dict by merging strategies and querying functionality.

    Merging strategies can define custom behavior how to merge certain values
    in the dict.

    Conditions can prevent merging a value under certain circumstances.

    Keys can be marked as finalizedd to avoid futur changes.

    Queries allow it to retrieve values deep inside the dict.
    """
    DEFAULT_STRING_QUERY_BUILDER = StringQueryBuilder

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
        self._annotations = {}
        init_values = __dct if __dct else {}
        init_values.update(kwargs)
        if isinstance(init_values, FancyDict):
            self.update(init_values)
        else:
            self.init_with_values(**init_values)

    def init_with_values(self, **init_values):
        for k, v in init_values.items():
            self[k] = v

    def annotate(self, key, annotations=None, **kwargs):
        annotations = Annotations(**kwargs) if annotations is None \
            else annotations
        if key in self._annotations:
            self._annotations[key].update(annotations)
        else:
            self._annotations[key] = annotations

    def get_annotations(self, key):
        return self._annotations.get(key, None)

    @property
    def strategies(self):
        return self._strategies

    def __setitem__(self, key, value):
        annotations = self.get_annotations(key)
        finalized = False if not annotations else annotations.finalized
        if not finalized:
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
        fancy_dict = dct if isinstance(dct, FancyDict) else type(self)(dct)
        for key in fancy_dict:
            self._update_value(key, fancy_dict)

    def _update_value(self, key, from_dict):
        old_value = self.get(key)
        new_value = from_dict.get(key)
        self.annotate(key, from_dict.get_annotations(key))
        annotations = self.get_annotations(key)
        if annotations.condition(old_value, new_value):
            if annotations.get("merge_method") is not None:
                self[key] = annotations.merge_method(old_value, new_value)
            else:
                strategies = self.strategies + from_dict.strategies
                for strategy in reversed(strategies):
                    if strategy.applies(old_value, new_value):
                        self[key] = strategy(old_value, new_value)
                        break
                else:
                    raise NoValidMergeStrategyFound(old_value, new_value)
