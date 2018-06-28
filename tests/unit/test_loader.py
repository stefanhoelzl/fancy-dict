import os
from pathlib import Path
from contextlib import contextmanager

import pytest
import json

from fancy_dict.loader import FileLoader, KeyAnnotationsConverter, DictLoader
from fancy_dict.errors import FileNotFoundInBaseDirs
from fancy_dict import conditions


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


class TestFileLoad:
    def test_single_file(self, tmpdir):
        with file_structure({"file.yml": {"a": 1}}, tmpdir):
            assert {"a": 1} == FileLoader([tmpdir]).load("file.yml")

    def test_single_file_in_directory(self, tmpdir):
        with file_structure({"dir": {"file.yml": {"a": 1}}}, tmpdir):
            assert {"a": 1} == FileLoader([tmpdir]).load("dir/file.yml")

    def test_single_file_multiple_bases(self, tmpdir):
        structure = {
            "dirA": {"fileA.yml": {"A": 1}},
            "dirB": {"fileB.yml": {"B": 1}},
        }
        with file_structure(structure, tmpdir):
            base_dirs = [Path(tmpdir) / "dirA", Path(tmpdir) / "dirB"]
            assert {"B": 1} == FileLoader(base_dirs).load("fileB.yml")

    def test_raise_file_not_found(self, tmpdir):
        with file_structure({"file.yml": {"a": 1}}, tmpdir):
            with pytest.raises(FileNotFoundInBaseDirs):
                FileLoader([tmpdir]).load("no_file.yml")

    def test_include_file(self, tmpdir):
        structure = {
            "file.yml": {"include": ["inc.yml"], "key": "value"},
            "inc.yml": {"inc_key": "value"}
        }
        with file_structure(structure, tmpdir):
            loader = FileLoader([tmpdir])
            result = {"key": "value", "inc_key": "value"}
            assert result == loader.load("file.yml")

    def test_include_order(self, tmpdir):
        structure = {
            "file.yml": {"include": ["inc.yml"], "A": 0},
            "inc.yml": {"A": "1"}
        }
        with file_structure(structure, tmpdir):
            assert {"A": 0} == FileLoader([tmpdir]).load("file.yml")

    def test_custom_include_key(self, tmpdir):
        structure = {
            "file.yml": {"custom_include": ["inc.yml"], "key": "value"},
            "inc.yml": {"inc_key": "value"}
        }
        with file_structure(structure, tmpdir):
            loader = FileLoader([tmpdir], include_key="custom_include")
            result = {"key": "value", "inc_key": "value"}
            assert result == loader.load("file.yml")

    def test_no_include_key(self, tmpdir):
        structure = {
            "file.yml": {"include": "value"}
        }
        with file_structure(structure, tmpdir):
            loader = FileLoader([tmpdir], include_key=None)
            result = {"include": "value"}
            assert result == loader.load("file.yml")

    def test_parse_annotations(self, tmpdir):
        structure = {
            "base.yml": {"(finalized)": True,
                         "counter": 1,
                         "sub": {"?yes": "YES"}},
            "file.yml": {"include": ["base.yml"],
                         "finalized": False,
                         "counter[add]": 3,
                         "sub": {"?no": "NO", "?yes": "YES"}
                         }
        }
        with file_structure(structure, tmpdir):
            loader = FileLoader([tmpdir])
            result = {"finalized": True, "counter": 4, "sub": {"yes": "YES"}}
            loaded = loader.load("file.yml")
            assert result == loaded


class TestDictLoader:
    def test_load(self):
        loader = DictLoader()
        assert {"a": 1} == loader.load({"a": 1})

    def test_parse_annotations(self):
        loader = DictLoader()
        assert {"a": 1} == loader.load(
            {"a": 1, "?b": 1}, annotations_decoder=KeyAnnotationsConverter
        )


class TestKeyAnnotationsConverter:
    def test_key_name_and_defaults(self):
        annotations = KeyAnnotationsConverter.decode(key="key")["annotations"]
        assert not annotations.finalized
        assert annotations.get("condition") is None
        assert annotations.get("merge_method") is None

    def test_finalized(self):
        annotations = KeyAnnotationsConverter.decode(key="(key)")["annotations"]
        assert annotations.finalized

    def test_custom_condition(self):
        annotations = KeyAnnotationsConverter.decode(key="+key")["annotations"]
        assert conditions.if_not_existing == annotations.condition

    def test_merge_method(self):
        key = "key[add]"
        annotations = KeyAnnotationsConverter.decode(key=key)["annotations"]
        assert 2 == annotations.merge_method(1, 1)

    def test_everything(self):
        key = "+(key)[add]"
        annotations = KeyAnnotationsConverter.decode(key=key)["annotations"]
        assert 2 == annotations.merge_method(1, 1)
        assert annotations.finalized

    @pytest.mark.parametrize("key", [
        "key",
        "(key)",
        "+key",
        "+key[add]",
        "+(key)[add]",
    ])
    def test_encoder(self, key):
        annotations = KeyAnnotationsConverter.decode(key=key)["annotations"]
        result = KeyAnnotationsConverter.encode(annotations, key="key")
        assert key == result["key"]
