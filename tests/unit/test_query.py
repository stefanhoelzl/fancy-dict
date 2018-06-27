from fancy_dict.query import QueryBuilder, StringQueryBuilder, Query, \
    Transformation


class TestStringQueryBuilder:
    def test_top_level_key(self):
        query = StringQueryBuilder("key").build()
        transformations = list(query)
        assert 1 == len(transformations)
        assert "get" == transformations[0].name
        assert "key" == transformations[0].args[0]

    def test_nested_key(self):
        query = StringQueryBuilder("key.middle.sub").build()
        transformations = list(query)
        assert 3 == len(transformations)
        assert "get" == transformations[0].name
        assert "get" == transformations[1].name
        assert "get" == transformations[2].name

    def test_match_all(self):
        query = StringQueryBuilder("key.*").build()
        transformations = list(query)
        assert 2 == len(transformations)
        assert "get" == transformations[0].name
        assert "all" == transformations[1].name

    def test_indexing(self):
        query = StringQueryBuilder("key[0:5:1]").build()
        transformations = list(query)
        assert 2 == len(transformations)
        assert "get" == transformations[0].name
        assert "slice" == transformations[1].name
        assert 0 == transformations[1].args[0]
        assert 5 == transformations[1].args[1]
        assert 1 == transformations[1].args[2]


class TestQuery:
    def test_add(self):
        query = Query()
        query.add(abs)
        query.add(all)
        assert [abs, all] == list(query)

    def test_apply_transformation_on_item(self):
        def capitalize(item):
            yield item.capitalize()

        query = Query()
        query.add(capitalize)
        assert ["Test"] == list(query.apply("test"))

    def test_apply_multiple_transformations_on_item(self):
        def upper(item):
            yield item.upper()

        def is_upper(item):
            yield item.isupper()

        query = Query()
        query.add(upper)
        query.add(is_upper)
        assert [True] == list(query.apply("test"))

    def test_empty_query(self):
        def transformation(item):
            if item:
                yield item

        query = Query()
        query.add(transformation)
        assert [] == list(query.apply(False))

    def test_transformation_with_multiple_results(self):
        def double(item):
            yield from [item]*2

        query = Query()
        query.add(double)
        query.add(double)
        assert ["a", "a", "a", "a"] == list(query.apply("a"))


class TestTransformation:
    def test_call(self):
        transformation = Transformation("get", "key")
        assert ["value"] == list(transformation({"key": "value"}))

    def test_get(self):
        assert ["value"] == list(Transformation.get({"key": "value"}, "key"))

    def test_all(self):
        dct = {"key0": "value0", "key1": "value1"}
        assert ["value0", "value1"] == list(Transformation.all(dct))

    def test_slice(self):
        result = list(Transformation.slice(list(range(10)), 2, 8, 3))
        assert [2, 5] == result


class TestQueryBuilder:
    def test_add_and_build(self):
        query = QueryBuilder().add("TRANSFORMATION").build()
        assert isinstance(query, Query)
        assert ["TRANSFORMATION"] == list(query)

    def test_add_transformation(self):
        query = QueryBuilder().all().build()
        assert "all" == next(iter(query)).name

