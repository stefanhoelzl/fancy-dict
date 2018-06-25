from fancy_dict.query_engine import QueryEngine, QueryBuilder, \
    StringQueryBuilder


def run_query(qry, dct):
    query_engine = QueryEngine()
    return list(query_engine(qry, dct))


class TestStringQueryBuilder:
    def test_top_level_key(self):
        query = StringQueryBuilder("key").build()
        filter_ = next(query)
        assert "get_" == filter_.__name__
        assert "key" == filter_.__closure__[0].cell_contents

    def test_nested_key(self):
        query = StringQueryBuilder("key.middle.sub").build()
        assert "get_" == next(query).__name__
        assert "get_" == next(query).__name__
        assert "get_" == next(query).__name__

    def test_match_all(self):
        query = StringQueryBuilder("key.*").build()
        assert "get_" == next(query).__name__
        assert "all_" == next(query).__name__

    def test_indexing(self):
        query = StringQueryBuilder("key[0:5:1]").build()
        assert "get_" == next(query).__name__
        filter_ = next(query)
        assert "slice_" == filter_.__name__
        assert 0 == filter_.__closure__[0].cell_contents
        assert 1 == filter_.__closure__[1].cell_contents
        assert 5 == filter_.__closure__[2].cell_contents


class TestQueryEngine:
    def test_no_match(self):
        query = QueryBuilder().get("no_key").build()
        assert [] == run_query(query, {"key": "value"})

    def test_top_level_key(self):
        query = QueryBuilder().get("key").build()
        assert ["value"] == run_query(query, {"key": "value"})

    def test_nested_no_match(self):
        query = QueryBuilder().get("key").get("sub").build()
        assert [] == run_query(query, {"key": {"middle": "value"}})

    def test_nested_key(self):
        query = QueryBuilder().get("key").get("middle").get("sub").build()
        assert ["value"] == run_query(query,
                                      {"key": {
                                          "middle": {
                                              "sub": "value"
                                          }
                                      }})

    def test_match_all(self):
        query = QueryBuilder().get("key").all().get("sub").build()
        assert ["v0", "v1"] == run_query(query,
                                         {"key": {
                                             "middle0": {
                                                 "sub": "v0"
                                             },
                                             "middle1": {
                                                 "sub": "v1"
                                             },
                                         }})

    def test_indexing(self):
        query = QueryBuilder().get("key").slice(-7, 9, 2).build()
        assert [3, 5, 7] == run_query(query,
                                      {"key": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]})

    def test_indexing_followed_by_key(self):
        query = QueryBuilder().get("key").slice(1).get("sub").build()
        assert ["value"] == run_query(query,
                                      {"key": [
                                          None,
                                          {"sub": "value"}
                                      ]})
