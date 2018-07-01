import pytest

from fancy_dict.merger import add, overwrite
from fancy_dict.conditions import if_existing, always
from fancy_dict.annotations import Annotations


class TestAnnotations:
    def test_defaults(self):
        annotations = Annotations()
        assert overwrite == annotations.merge_method
        assert always == annotations.condition
        assert not annotations.finalized

    def test_get_none(self):
        annotations = Annotations()
        assert annotations.get("condition") is None

    def test_default_if_none_was_set(self):
        annotations = Annotations(condition=None)
        assert always == annotations.condition

    def test_update_merge_method(self):
        annotations = Annotations(
            merge_method=add, finalized=True, condition=if_existing
        )
        annotations.update(Annotations(merge_method=overwrite))
        assert overwrite == annotations.merge_method
        assert annotations.finalized
        assert if_existing == annotations.condition

    def test_update_finalized(self):
        annotations = Annotations(
            merge_method=add, finalized=False, condition=if_existing
        )
        annotations.update(Annotations(finalized=True))
        assert add == annotations.merge_method
        assert annotations.finalized
        assert if_existing == annotations.condition

    def test_update_condition(self):
        annotations = Annotations(
            merge_method=add, finalized=False, condition=if_existing
        )
        annotations.update(Annotations(condition=always))
        assert add == annotations.merge_method
        assert not annotations.finalized
        assert always == annotations.condition

    def test_attribute_error_if_not_in_defaults(self):
        with pytest.raises(AttributeError):
            assert not Annotations().no_attribute
