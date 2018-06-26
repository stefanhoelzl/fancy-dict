from unittest import mock

from fancy_dict.query_engine import QueryBuilder, StringQueryBuilder


def run_query(query, dct):
    return list(query.apply(dct))


class TestStringQueryBuilder:
    def test_top_level_key(self):
        with mock.patch.object(StringQueryBuilder, "add") as add_mock:
            StringQueryBuilder("key").build()
        add_mock.assert_called_once()
        transformation = add_mock.call_args[0][0]
        assert "_get" == transformation.__name__
        assert "key" == transformation.__closure__[0].cell_contents

    def test_nested_key(self):
        with mock.patch.object(StringQueryBuilder, "add") as add_mock:
            StringQueryBuilder("key.middle.sub").build()
        assert 3 == add_mock.call_count
        assert "_get" == add_mock.call_args_list[0][0][0].__name__
        assert "_get" == add_mock.call_args_list[1][0][0].__name__
        assert "_get" == add_mock.call_args_list[2][0][0].__name__

    def test_match_all(self):
        with mock.patch.object(StringQueryBuilder, "add") as add_mock:
            StringQueryBuilder("key.*").build()
        assert 2 == add_mock.call_count
        assert "_get" == add_mock.call_args_list[0][0][0].__name__
        assert "_all" == add_mock.call_args_list[1][0][0].__name__

    def test_indexing(self):
        with mock.patch.object(StringQueryBuilder, "add") as add_mock:
            StringQueryBuilder("key[0:5:1]").build()
        assert 2 == add_mock.call_count
        assert "_get" == add_mock.call_args_list[0][0][0].__name__
        slice_ = add_mock.call_args_list[1][0][0]
        assert "_slice" == slice_.__name__
        assert 0 == slice_.__closure__[0].cell_contents
        assert 1 == slice_.__closure__[1].cell_contents
        assert 5 == slice_.__closure__[2].cell_contents


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
