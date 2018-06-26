"""FancyDict QueryEngine"""

import re
from itertools import chain


class Query:
    """Query

    Sequence of transformations.
    Can be applied onto a object to receive a result.

    A transformation gets a object as parameter
    and returns the transformed object.
    """
    def __init__(self):
        self._transformations = []
        self._current_transformation = 0

    def add(self, transformation):
        """Adds a transformation

        Args:
            transformation: transformation to add
        """
        self._transformations.append(transformation)

    def apply(self, item):
        """Applies the transformations onto a given object

        Args:
            item: item to apply the transformations onto

        Returns:
            transformed item
        """
        transformed = (item,)
        for transformation in self._transformations:
            transformed = chain.from_iterable(map(transformation, transformed))
        yield from transformed


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

    def get(self, key):
        """Transformation to query the key of an dict

        Args:
            key: key to query from dict

        Returns:
            QueryBuilder
        """
        def _get(item):
            if key in item:
                yield item.get(key)
        self.add(_get)
        return self

    def slice(self, start=None, stop=None, step=None):
        """Transformation to get a slice of an sequence

        Args:
            start: start of slice
            stop: end of slice
            step: steps of slice

        Returns:
            QueryBuilder
        """
        def _slice(item):
            yield from item[slice(start, stop, step)]
        self.add(_slice)
        return self

    def all(self):
        """Transformation to query all values of a dict

        Returns:
            QueryBuilder
        """
        def _all(item):
            yield from item.values()
        self.add(_all)
        return self


class StringQueryBuilder(QueryBuilder):
    """Builds a Query from a string definition.
    """
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
