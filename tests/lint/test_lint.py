import pycodestyle
import pylint.lint
import mypy.api


def test_codestyle():
    style = pycodestyle.StyleGuide()
    result = style.check_files(paths=["fancy_dict"])
    assert 0 == result.total_errors


def test_pylint():
    args = ["--disable=R0903",  # too-few-public-methods
            "--disable=R0401",  # cyclic-import
            "fancy_dict"]
    assert 0 == pylint.lint.Run(args, exit=False).linter.msg_status


def test_mypy():
    out, err, result = mypy.api.run(["fancy_dict", "--strict"])
    print(out)
    print(err)
    assert 0 == result
