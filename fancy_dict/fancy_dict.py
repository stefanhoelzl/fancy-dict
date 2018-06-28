"""A FancyDict is a dict with extended merging and querying functionality."""

from . import merger
from .errors import NoValidMergeStrategyFound
from .query import StringQueryBuilder, Query
from .conditions import always
from .loader import Loader


class Annotations:
    """Annotations for a FancyDict key

    Composed of a merge strategy, a merge condition and if the key is finalized
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

    Keys can be marked as finalizedd to avoid future updates.

    Queries allow it to retrieve values deep inside the dict.
    """
    MERGE_STRATEGIES = (
        merger.MergeStrategy(merger.update,
                             from_types=dict, to_types=dict),
        merger.MergeStrategy(merger.overwrite),
    )

    @classmethod
    def load(cls, item, loader=Loader, **kwargs):
        if isinstance(item, FancyDict):
            return item
        else:
            return loader(cls, **kwargs).load(item)

    def __init__(self, __dct=None, **kwargs):
        super().__init__()
        self._annotations = {}
        self.update(__dct, **kwargs)

    def annotate(self, key, annotations=None, **kwargs):
        if annotations or kwargs:
            annotations = Annotations(**kwargs) if annotations is None \
                else annotations
            if key in self._annotations:
                self._annotations[key].update(annotations)
            else:
                self._annotations[key] = annotations

    def get_annotations(self, key, default=None):
        return self._annotations.get(key, default)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = self.load(value)
        super().__setitem__(key, value)

    def query(self, query, query_builder=StringQueryBuilder):
        """Runs a query on the FancyDict

        Args:
            query: query to run

        Returns:
            query results
        """
        if not isinstance(query, Query):
            query = query_builder(query).build()
        return query.apply(self)

    def update(self, __dct=None, **kwargs):
        """Updates the FancyDict using the given merging strategies."""
        if isinstance(__dct, dict):
            self._update_with_fancy_dict(self.load(__dct))
        if kwargs:
            self._update_with_fancy_dict(self.load(kwargs))

    def _update_with_fancy_dict(self, fancy_dict):
        for key in fancy_dict:
            self._update_value(key, fancy_dict)

    def _update_value(self, key, from_dict):
        if self.get_annotations(key, Annotations()).finalized:
            return

        old_value = self.get(key)
        new_value = from_dict.get(key)
        self.annotate(key, from_dict.get_annotations(key))
        annotations = self.get_annotations(key, Annotations())
        if annotations.condition(old_value, new_value):
            if annotations.get("merge_method") is not None:
                self[key] = annotations.merge_method(old_value, new_value)
            else:
                strategies = from_dict.MERGE_STRATEGIES + self.MERGE_STRATEGIES
                for strategy in strategies:
                    if strategy.applies(old_value, new_value):
                        self[key] = strategy(old_value, new_value)
                        break
                else:
                    raise NoValidMergeStrategyFound(old_value, new_value)
