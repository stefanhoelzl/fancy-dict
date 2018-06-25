from pycodestyle import StyleGuide


def test_codestyle():
    style = StyleGuide()
    result = style.check_files(paths=["fancy_dict"])
    assert 0 == result.total_errors
