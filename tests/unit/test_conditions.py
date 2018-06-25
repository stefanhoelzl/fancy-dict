from fancy_dict.conditions import always, if_existing, if_not_existing


class TestAlways:
    def test_always_true(self):
        assert always(None, None) is True
        assert always("old", "new") is True
        assert always("old", None) is True
        assert always(None, "new") is True


class TestIfExisting:
    def test_false_if_old_is_none(self):
        assert if_existing(None, "new") is False

    def test_true_if_old_is_not_none(self):
        assert if_existing("old", "new") is True


class TestIfNotExisting:
    def test_true_if_old_is_none(self):
        assert if_not_existing(None, "new") is True

    def test_false_if_old_is_not_none(self):
        assert if_not_existing("old", "new") is False
