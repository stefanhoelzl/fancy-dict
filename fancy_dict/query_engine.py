import re
import typing
from contextlib import contextmanager


class Query:
    def __init__(self):
        self._filter = []
        self._current_filter = 0

    def add(self, filter_):
        self._filter.append(filter_)

    @contextmanager
    def _tee(self):
        current_filter_backup = self._current_filter
        yield
        self._current_filter = current_filter_backup

    def __bool__(self):
        return self._current_filter < len(self._filter)

    def __next__(self):
        if self:
            _filter = self._filter[self._current_filter]
            self._current_filter += 1
            return _filter
        raise StopIteration

    def __call__(self, item):
        with self._tee():
            filter_ = self.__next__()
            yield from filter_(item)


class QueryBuilder:
    def __init__(self):
        self._query = Query()

    def build(self):
        return self._query

    def add(self, filter_):
        self._query.add(filter_)

    def get(self, key):
        def get_(item):
            yield item.get(key)
        self.add(get_)
        return self

    def slice(self, start=None, stop=None, step=None):
        def slice_(item):
            yield from item[slice(start, stop, step)]
        self.add(slice_)
        return self

    def all(self):
        def all_(item):
            yield from item.values()
        self.add(all_)
        return self


class StringQueryBuilder(QueryBuilder):
    def __init__(self, query_string,
                 separator=".",
                 indexing="^(?P<key>.*)\[(?P<index>[0-9-:]*)\]$",
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


class QueryEngine:
    def __call__(self, query, item):
        if isinstance(query, str):
            query = StringQueryBuilder(query).build()
        yield from self._run_query(query, item)

    def _run_query(self, query, item):
        if not query:
            yield from self._iter_item(item)
        else:
            for new_item in query(item):
                yield from self(query, new_item)

    @staticmethod
    def _iter_item(item):
        if isinstance(item, typing.Sequence) and not isinstance(item, str):
            yield from item
        elif item is not None:
            yield item
