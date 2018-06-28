from fancy_dict.merger import MergeStrategy, overwrite, update, add


class TestApplies:
    def test_false_if_no_condition_true(self):
        merger = MergeStrategy(overwrite, from_types=(str,), to_types=(str,))
        assert not merger.applies(1, 2)

    def test_true_if_all_conditions_none(self):
        assert MergeStrategy(overwrite).applies(1, 2)

    def test_true_if_from_types_matches(self):
        merger = MergeStrategy(overwrite, from_types=(int, str))
        assert merger.applies(1, [1])
        assert merger.applies("old", (1,))

    def test_true_if_to_types_matches(self):
        merger = MergeStrategy(overwrite, to_types=(int, str))
        assert merger.applies([1], 1)
        assert merger.applies((1,), "new")


class TestMethods:
    def test_overwrite(self):
        assert "NEW" == overwrite("OLD", "NEW")

    def test_update(self):
        old = {"a": 1, "b": 1}
        new = {"a": 0, "c": 2}
        assert {"a": 0, "b": 1, "c": 2} == update(old, new)

    def test_add(self):
        assert [1, 2, 3, 4] == add([1, 2], [3, 4])
        assert "OLDNEW" == add("OLD", "NEW")
        assert 3 == add(1, 2)
