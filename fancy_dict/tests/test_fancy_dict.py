from ..fancy_dict import FancyDict


class TestInit:
    def test_with_dict(self):
        assert FancyDict({"a": 1}) == {"a": 1}

    def test_with_keywords(self):
        assert FancyDict(a=1) == {"a": 1}

    def test_convert_nested_dict_to_fancy_dict(self):
        assert isinstance(FancyDict(dct={"sub": 1})["dct"], FancyDict)


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


class TestSetItem:
    def test_convert_dict_to_fancy_dict(self):
        fancy_dict = FancyDict()
        fancy_dict["dict"] = {"key": "value"}
        assert isinstance(fancy_dict["dict"], FancyDict)
