from ..merger import *


class TestOverwrite:
    def test_return_new(self):
        assert "NEW" == overwrite("OLD", "NEW")


class TestUpdate:
    def test_update_new(self):
        old = {"a": 1, "b": 1}
        new = {"a": 0, "c": 2}
        assert {"a": 0, "b": 1, "c": 2} == update(old, new)


class TestExtend:
    def test_update_new(self):
        old = [1, 2]
        new = [3, 4]
        assert [1, 2, 3, 4] == extend(old, new)
