import pytest

from fancy_dict import FancyDict
from fancy_dict.errors import NoMergeMethodApplies
from fancy_dict.merger import MergeMethod, add
from fancy_dict.annotations import Annotations


def fancy_dict_with_merge_methods(*methods, extend=False):
    base = FancyDict.MERGE_METHODS if extend else ()

    class _FancyDict(FancyDict):
        MERGE_METHODS = methods + base

    return _FancyDict()


class TestInit:
    def test_with_dict(self):
        assert {"a": 1} == FancyDict({"a": 1})

    def test_with_keywords(self):
        assert {"a": 1} == FancyDict(a=1)

    def test_keywords_overwrite_dict(self):
        assert {"a": 1} == FancyDict({"a": 0}, a=1)

    def test_convert_nested_dict_to_fancy_dict(self):
        assert isinstance(FancyDict(dct={"sub": 1})["dct"], FancyDict)


class TestLoad:
    def test_load_dict(self):
        fancy_dict = FancyDict.load({"a": 1})
        assert {"a": 1} == fancy_dict


class TestSetItem:
    def test_convert_dict_to_fancy_dict(self):
        fancy_dict = FancyDict()
        fancy_dict["dict"] = {"key": "value"}
        assert isinstance(fancy_dict["dict"], FancyDict)

    def test_use_same_merge_method_when_converting_dict(self):
        fancy_dict = fancy_dict_with_merge_methods(
            MergeMethod(add, from_types=int),
            extend=True
        )
        fancy_dict["counters"] = {"a": 1}
        fancy_dict.update(counters={"a": 1})
        assert 2 == fancy_dict["counters"]["a"]

    def test_allow_change_even_if_finalized(self):
        fancy_dict = FancyDict(finalized=1)
        fancy_dict.annotate("finalized",  Annotations(finalized=True))
        fancy_dict["finalized"] = 2
        assert 2 == fancy_dict["finalized"]


class TestAnnotate:
    def test_set_condition(self):
        fancy_dict = FancyDict()
        fancy_dict["key"] = "value"
        fancy_dict["key_not_merging"] = "value"
        fancy_dict.annotate("key_not_merging",
                            Annotations(condition=lambda o, n: False))
        assert {"key": "value"} == FancyDict(fancy_dict)

    def test_finalized(self):
        fancy_dict = FancyDict(finalized=1)
        fancy_dict.annotate("finalized",  Annotations(finalized=True))
        fancy_dict.update(finalized=2)
        assert 1 == fancy_dict["finalized"]

    def test_merge_method(self):
        base_dict = FancyDict()
        base_dict["counter"] = 1
        update_dict = FancyDict(counter=1)
        update_dict.annotate("counter", Annotations(merge_method=add))
        base_dict.update(update_dict)
        assert 2 == base_dict["counter"]

    def test_create_annotations_from_keyword_arguments(self):
        fancy_dict = FancyDict(finalized=1)
        fancy_dict.annotate("finalized", finalized=True)
        fancy_dict.update(finalized=2)
        assert 1 == fancy_dict["finalized"]

        fancy_dict["key"] = "value"
        fancy_dict["key_not_merging"] = "value"
        fancy_dict.annotate("key_not_merging", condition=lambda o, n: False)
        assert "key_not_merging" not in FancyDict(fancy_dict)

        fancy_dict["counter"] = 1
        update_dict = FancyDict(counter=1)
        update_dict.annotate("counter", merge_method=add)
        fancy_dict.update(update_dict)
        assert 2 == fancy_dict["counter"]

    def test_update_existing_annotations(self):
        annotations = Annotations(finalized=True)
        fancy_dict = FancyDict(key=1)
        fancy_dict.annotate("key", annotations)
        fancy_dict.annotate("key", finalized=False)
        assert not annotations.finalized

    def test_dont_set_annotations_when_there_are_none(self):
        fancy_dict = FancyDict(key=1)
        fancy_dict.annotate("key", None)
        assert fancy_dict.get_annotations("key") is None


class TestUpdateWithDict:
    def test_updates_nested_dicts(self):
        base_dict = FancyDict({
            "base": {
                "key0": 0
            }
        })
        update_dict = {
            "base": {
                "key1": 1
            }
        }
        base_dict.update(update_dict)
        assert {
            "base": {
                "key0": 0,
                "key1": 1
            }
        } == base_dict

    def test_overwrite_dict_with_another_type(self):
        base_dict = FancyDict({"base": {"sub": 1}})
        base_dict.update({"base": 0})
        assert {"base": 0} == base_dict

    def test_with_keyword_arguments(self):
        base_dict = FancyDict({})
        base_dict.update(key=1)
        assert {"key": 1} == base_dict

    def test_raise_if_no_valid_merge_method(self):
        fancy_dict = fancy_dict_with_merge_methods()
        with pytest.raises(NoMergeMethodApplies) as e:
            fancy_dict.update(val=1)
        assert e.value.old_value is None
        assert 1 == e.value.new_value


class TestUpdateWithFancyDict:
    def test_use_different_merge_methods_only_once(self):
        base_fancy_dict = FancyDict(counter=1)
        update_fancy_dict = fancy_dict_with_merge_methods(
            MergeMethod(add)
        )
        update_fancy_dict["counter"] = 1
        base_fancy_dict.update(update_fancy_dict)
        assert 2 == base_fancy_dict["counter"]
        base_fancy_dict.update(counter=1)
        assert 1 == base_fancy_dict["counter"]

    def test_update_annotations(self):
        annotations = Annotations(finalized=True)
        updating_fancy_dict = FancyDict(key=1)
        updating_fancy_dict.annotate("key", annotations)
        base_fancy_dict = FancyDict()
        base_fancy_dict.update(updating_fancy_dict)
        assert base_fancy_dict.get_annotations("key").finalized

    def test_if_finalized_dont_update_annotations(self):
        fancy_dict = FancyDict(key=1)
        fancy_dict.annotate("key", finalized=True)
        update = FancyDict(key=2)
        update.annotate("key", finalized=False)
        fancy_dict.update(update)
        assert 1 == fancy_dict["key"]


class TestQuery:
    def test_query_string(self):
        fancy_dict = FancyDict({"key": {"sub": 1}})
        assert 1 == next(fancy_dict.query("key.sub"))
