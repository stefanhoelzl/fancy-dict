import os
from pathlib import Path
from contextlib import contextmanager

import pytest
import json

from fancy_dict.serialize import Loader
from fancy_dict.errors import FileNotFoundInBaseDirs


@contextmanager
def chdir(new_dir):
    old_dir = os.getcwd()
    os.chdir(new_dir)
    yield
    os.chdir(old_dir)


def create_file_structure(base, structure):
    for file_or_folder, content in structure.items():
        if file_or_folder.endswith(".yml"):
            base.join(file_or_folder).write(json.dumps(content, indent=2))
        else:
            create_file_structure(base.mkdir(file_or_folder), content)


@contextmanager
def file_structure(structure, tmpdir):
    create_file_structure(tmpdir, structure)
    with chdir(tmpdir):
        yield


class TestLoad:
    def test_single_file(self, tmpdir):
        with file_structure({"file.yml": {"a": 1}}, tmpdir):
            assert {"a": 1} == Loader([tmpdir]).load("file.yml")

    def test_single_file_in_directory(self, tmpdir):
        with file_structure({"dir": {"file.yml": {"a": 1}}}, tmpdir):
            assert {"a": 1} == Loader([tmpdir]).load("dir/file.yml")

    def test_single_file_multiple_bases(self, tmpdir):
        structure = {
            "dirA": {"fileA.yml": {"A": 1}},
            "dirB": {"fileB.yml": {"B": 1}},
        }
        with file_structure(structure, tmpdir):
            base_dirs = [Path(tmpdir) / "dirA", Path(tmpdir) / "dirB"]
            assert {"B": 1} == Loader(base_dirs).load("fileB.yml")

    def test_raise_file_not_found(self, tmpdir):
        with file_structure({"file.yml": {"a": 1}}, tmpdir):
            with pytest.raises(FileNotFoundInBaseDirs):
                Loader([tmpdir]).load("no_file.yml")

    def test_include_file(self, tmpdir):
        structure = {
            "file.yml": {"include": ["inc.yml"], "key": "value"},
            "inc.yml": {"inc_key": "value"}
        }
        with file_structure(structure, tmpdir):
            loader = Loader([tmpdir])
            result = {"key": "value", "inc_key": "value"}
            assert result == loader.load("file.yml")

    def test_include_order(self, tmpdir):
        structure = {
            "file.yml": {"include": ["inc.yml"], "A": 0},
            "inc.yml": {"A": "1"}
        }
        with file_structure(structure, tmpdir):
            assert {"A": 0} == Loader([tmpdir]).load("file.yml")

    def test_custom_include_key(self, tmpdir):
        structure = {
            "file.yml": {"custom_include": ["inc.yml"], "key": "value"},
            "inc.yml": {"inc_key": "value"}
        }
        with file_structure(structure, tmpdir):
            loader = Loader([tmpdir], include_key="custom_include")
            result = {"key": "value", "inc_key": "value"}
            assert result == loader.load("file.yml")

    def test_no_include_key(self, tmpdir):
        structure = {
            "file.yml": {"include": "value"}
        }
        with file_structure(structure, tmpdir):
            loader = Loader([tmpdir], include_key=None)
            result = {"include": "value"}
            assert result == loader.load("file.yml")
