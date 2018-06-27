"""FancyDict QueryEngine"""

import re
from itertools import chain
from functools import partial


class Query:
    """Query

    Sequence of transformations.
    Can be applied onto a object to receive a result.

    A transformation gets a object as parameter
    and returns the transformed object.
    """
    def __init__(self):
        self._transformations = []

    def add(self, transformation):
        """Adds a transformation

        Args:
            transformation: transformation to add
        """
        self._transformations.append(transformation)

    def __iter__(self):
        return iter(self._transformations)

    def apply(self, item):
        """Applies the transformations onto a given object

        Args:
            item: item to apply the transformations onto

        Returns:
            transformed item
        """
        transformed = (item,)
        for transformation in self:
            transformed = chain.from_iterable(map(transformation, transformed))
        yield from transformed


class Transformation:
    """Wrapper class for methods which transforms items for a Query"""
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.args = args
        self.kwargs = kwargs

    def __call__(self, item):
        method = getattr(self, self.name)
        yield from method(item, *self.args, **self.kwargs)

    @staticmethod
    def get(item, key):
        """Transformation to query the key of an dict

        Args:
            item: item to transform
            key: key to query from dict

        Returns:
            value for key
        """
        if key in item:
            yield item.get(key)

    @staticmethod
    def slice(item, start=None, stop=None, step=None):
        """Transformation to get a slice of an sequence

        Args:
            item: item to transform
            start: start of slice
            stop: end of slice
            step: steps of slice

        Yields:
            sub-items in slice
        """
        yield from item[slice(start, stop, step)]

    @staticmethod
    def all(item):
        """Transformation to query all values of a dict

        Args:
            item: item to transform

        Yields:
            item values
        """
        yield from item.values()


class QueryBuilder:
    """QueryBuilder

    Builds a Query by chaining transformations.
    """
    def __init__(self):
        self._query = Query()

    def build(self):
        """Builds the Query

        Returns:
            the Query
        """
        return self._query

    def add(self, transformation):
        """Adds a transformation to the Query

        Args:
            transformation: transformation to add
        """
        self._query.add(transformation)
        return self

    def _add(self, name, *args, **kwargs):
        return self.add(Transformation(name, *args, **kwargs))

    def __getattr__(self, item):
        if hasattr(Transformation, item):
            return partial(self._add, item)
        return super().__getattribute__(item)


class StringQueryBuilder(QueryBuilder):
    """Builds a Query from a string definition."""
    def __init__(self, query_string,
                 separator=".",
                 indexing=r"^(?P<key>.*)\[(?P<index>[0-9-:]*)\]$",
                 match_all="*"):
        super().__init__()
        self._separator = separator
        self._indexing = indexing
        self._match_all = match_all
        self._resolve_query_string(query_string)

    @staticmethod
    def _pop_from_slice_list(slice_list):
        return int(slice_list.pop(0)) if slice_list and slice_list[0] != "" \
            else None

    def _get_slice(self, key):
        match = re.match(self._indexing, key)
        if match:
            key, index = match.group("key"), match.group("index").split(":")
            start = self._pop_from_slice_list(index)
            stop = self._pop_from_slice_list(index)
            step = self._pop_from_slice_list(index)
            return key, (start, stop, step)
        return key, None

    def _key(self, key):
        if key == self._match_all:
            self.all()
        else:
            self.get(key)

    def _separate_query_string(self, query_string):
        if self._separator not in query_string:
            return query_string, None
        return query_string.split(self._separator, 1)

    def _resolve_query_string(self, query_string):
        key, sub_query_string = self._separate_query_string(query_string)
        key, slice_ = self._get_slice(key)
        self._key(key)
        if slice_:
            self.slice(*slice_)
        if sub_query_string:
            self._resolve_query_string(sub_query_string)
