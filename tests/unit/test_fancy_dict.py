import pytest

from fancy_dict import FancyDict
from fancy_dict.errors import NoValidMergeStrategyFound
from fancy_dict.merger import MergeStrategy, add, overwrite


class TestUsingStrategies:
    def test_use_given_strategies(self):
        fancy_dict = FancyDict.using_strategies(MergeStrategy(add))
        fancy_dict["counter"] = 1
        fancy_dict.update(counter=1)
        assert 2 == fancy_dict["counter"]

    def test_init_with_dict(self):
        assert {"a": 1} == FancyDict.using_strategies(init_with={"a": 1})


class TestInit:
    def test_with_dict(self):
        assert {"a": 1} == FancyDict({"a": 1})

    def test_with_keywords(self):
        assert {"a": 1} == FancyDict(a=1)

    def test_convert_nested_dict_to_fancy_dict(self):
        assert isinstance(FancyDict(dct={"sub": 1})["dct"], FancyDict)


class TestSetItem:
    def test_convert_dict_to_fancy_dict(self):
        fancy_dict = FancyDict()
        fancy_dict["dict"] = {"key": "value"}
        assert isinstance(fancy_dict["dict"], FancyDict)

    def test_use_same_strategies_when_converting_dict(self):
        fancy_dict = FancyDict()
        fancy_dict.add_strategy(MergeStrategy(add, from_types=int))
        fancy_dict["counters"] = {"a": 1}
        fancy_dict.update(counters={"a": 1})
        assert 2 == fancy_dict["counters"]["a"]


class TestDerive:
    def test_copy_strategies(self):
        base_fancy_dict = FancyDict.using_strategies(MergeStrategy(add))
        derived_fancy_dict = base_fancy_dict.derive(init_with={"counter": 1})
        derived_fancy_dict.update(counter=1)
        assert 2 == derived_fancy_dict["counter"]

    def test_ignore_strategies_with_key(self):
        base_fancy_dict = FancyDict.using_strategies(
            MergeStrategy(overwrite), MergeStrategy(add, key="key")
        )
        derived_fancy_dict = base_fancy_dict.derive(init_with={"key": 1})
        derived_fancy_dict.update(key=3)
        assert 3 == derived_fancy_dict["key"]

    def test_init_with_dict(self):
        fancy_dict = FancyDict().derive(init_with={"a": 1})
        assert {"a": 1} == fancy_dict


class TestAddStrategy:
    def test_add_and_use_new_strategy(self):
        fancy_dict = FancyDict()
        fancy_dict["counter"] = 1
        fancy_dict.add_strategy(MergeStrategy(add, key="counter"))
        fancy_dict.update(counter=1)
        assert 2 == fancy_dict["counter"]


class TestClearStrategies:
    def test_clear_strategies(self):
        fancy_dict = FancyDict()
        fancy_dict.clear_strategies()
        assert 0 == len(fancy_dict.strategies)


class TestAddCondition:
    def test_add_and_use_condition(self):
        fancy_dict_with_condition = FancyDict()
        fancy_dict_with_condition["key"] = "value"
        fancy_dict_with_condition["key_not_merging"] = "value"
        fancy_dict_with_condition.set_condition("key_not_merging",
                                                lambda o, n: False)
        assert {"key": "value"} == FancyDict(fancy_dict_with_condition)


class TestFinalize:
    def test_dont_change_value_if_locked(self):
        fancy_dict = FancyDict(locked=1)
        fancy_dict.finalize("locked")
        fancy_dict["locked"] = 2
        assert 1 == fancy_dict["locked"]


class TestUpdate:
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

    def test_raise_if_no_valid_strategy(self):
        fancy_dict = FancyDict.using_strategies()
        with pytest.raises(NoValidMergeStrategyFound) as e:
            fancy_dict.update(val=1)
        assert "val" == e.value.key
        assert e.value.old_value is None
        assert 1 == e.value.new_value

    def test_use_strategy_of_new_fancy_dict(self):
        base_fancy_dict = FancyDict(counter=1)
        update_fancy_dict = FancyDict.using_strategies(
            MergeStrategy(add), init_with={"counter": 1}
        )
        base_fancy_dict.update(update_fancy_dict)
        assert 2 == base_fancy_dict["counter"]


class TestQuery:
    def test_query_string(self):
        fancy_dict = FancyDict({"key": {"sub": 1}})
        assert 1 == next(fancy_dict.query("key.sub"))
