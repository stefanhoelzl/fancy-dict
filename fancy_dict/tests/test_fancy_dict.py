from ..fancy_dict import FancyDict


def test_update_updatesNestedDicts():
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


def test_update_overwriteDictWithAnotherType():
    base_dict = FancyDict({"base": {"sub": 1}})
    base_dict.update({"base": 0})
    assert {"base": 0} == base_dict


def test_update_withKeywordArguments():
    base_dict = FancyDict({})
    base_dict.update(key=1)
    assert {"key": 1} == base_dict
