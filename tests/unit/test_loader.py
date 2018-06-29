import os
from pathlib import Path
from contextlib import contextmanager
from io import StringIO

import pytest
import json

from fancy_dict.loader import CompositeLoader, FileLoader, DictLoader, \
    KeyAnnotationsConverter, HttpLoader, IoLoader
from fancy_dict.errors import NoLoaderForSourceAvailable
from fancy_dict import conditions, FancyDict


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


class TestFileLoader:
    def test_single_file(self, tmpdir):
        with file_structure({"file.yml": {"a": 1}}, tmpdir):
            assert {"a": 1} == FileLoader(FancyDict).load("file.yml")

    def test_single_file_in_directory(self, tmpdir):
        with file_structure({"dir": {"file.yml": {"a": 1}}}, tmpdir):
            assert {"a": 1} == FileLoader(FancyDict).load("dir/file.yml")

    def test_raise_file_not_found(self, tmpdir):
        with file_structure({"file.yml": {"a": 1}}, tmpdir):
            with pytest.raises(FileNotFoundError):
                FileLoader(FancyDict).load("no_file.yml")

    def test_raise_file_not_found_but_in_bases(self, tmpdir):
        structure = {
            "inc": {"file.yml": {"include": ["inc.yml"], "key": "value"}}
        }
        with file_structure(structure, tmpdir):
            with pytest.raises(FileNotFoundError):
                FileLoader(FancyDict, include_paths=("inc",)).load("file.yml")

    def test_raise_include_file_not_found(self, tmpdir):
        structure = {
            "file.yml": {"include": ["inc.yml"], "key": "value"}
        }
        with file_structure(structure, tmpdir):
            with pytest.raises(FileNotFoundError):
                FileLoader(FancyDict, include_key="include").load("file.yml")

    def test_include_file(self, tmpdir):
        structure = {
            "file.yml": {"include": ["inc.yml"], "key": "value"},
            "inc.yml": {"inc_key": "value"}
        }
        with file_structure(structure, tmpdir):
            loader = FileLoader(FancyDict, include_key="include")
            result = {"key": "value", "inc_key": "value"}
            assert result == loader.load("file.yml")

    def test_include_order(self, tmpdir):
        structure = {
            "file.yml": {"include": ["inc.yml"], "A": 0},
            "inc.yml": {"A": "1"}
        }
        with file_structure(structure, tmpdir):
            loader = FileLoader(FancyDict, include_key="include")
            assert {"A": 0} == loader.load("file.yml")

    def test_custom_include_key(self, tmpdir):
        structure = {
            "file.yml": {"custom_include": ["inc.yml"], "key": "value"},
            "inc.yml": {"inc_key": "value"}
        }
        with file_structure(structure, tmpdir):
            loader = FileLoader(FancyDict, include_key="custom_include")
            result = {"key": "value", "inc_key": "value"}
            assert result == loader.load("file.yml")

    def test_no_include_key(self, tmpdir):
        structure = {
            "file.yml": {"include": "value"}
        }
        with file_structure(structure, tmpdir):
            loader = FileLoader(FancyDict, include_key=None)
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
            loader = FileLoader(FancyDict, include_key="include")
            result = {"finalized": True, "counter": 4, "sub": {"yes": "YES"}}
            loaded = loader.load("file.yml",
                                 annotations_decoder=KeyAnnotationsConverter)
            assert result == loaded

    def test_can_load(self, tmpdir):
        structure = {
            "base": {"file.yml": {"key": "value"}}
        }
        with file_structure(structure, tmpdir):
            assert FileLoader.can_load(Path("base", "file.yml"))
            assert not FileLoader.can_load("file.yml")

    def test_can_load_false_if_url(self):
        assert not FileLoader.can_load("http://www.test.de")


class TestDictLoader:
    def test_load(self):
        loader = DictLoader(FancyDict)
        assert {"a": 1} == loader.load({"a": 1})

    def test_parse_annotations(self):
        loader = DictLoader(FancyDict)
        assert {"a": 1} == loader.load(
            {"a": 1, "?b": 1}, annotations_decoder=KeyAnnotationsConverter
        )

    def test_can_load(self):
        assert DictLoader.can_load({})
        assert not DictLoader.can_load("no")


class TestHttpLoader:
    def test_load(self, httpserver):
        httpserver.serve_content("{'a': 1}")
        assert {"a": 1} == HttpLoader(FancyDict).load(httpserver.url)

    def test_can_load(self, httpserver):
        httpserver.serve_content("{'a': 1}")
        assert HttpLoader.can_load(httpserver.url)

    def test_can_load_https(self):
        assert HttpLoader.can_load("https://www.google.de")


class TestIoLoader:
    def test_can_load(self):
        assert IoLoader.can_load(StringIO(""))

    def test_load(self):
        assert {"a": 1} == IoLoader(FancyDict).load(StringIO('{"a": 1}'))


class TestCompositeLoader:
    def test_load_dict(self):
        loader = CompositeLoader(FancyDict)
        assert {"a": 1} == loader.load({"a": 1})

    def test_load_from_http(self, httpserver):
        httpserver.serve_content("{'a': 1}")
        assert {"a": 1} == CompositeLoader(FancyDict).load(httpserver.url)

    def test_load_from_file(self, tmpdir):
        with file_structure({"file.yml": {"a": 1}}, tmpdir):
            assert {"a": 1} == CompositeLoader(FancyDict).load("file.yml")

    def test_raise_when_no_loader_available(self):
        with pytest.raises(NoLoaderForSourceAvailable):
            CompositeLoader(FancyDict).load("no_file")

    def test_load_from_io_object(self):
        data_string = StringIO('{"a": 1}')
        assert {"a": 1} == CompositeLoader(FancyDict).load(data_string)

    def test_pass_args_to_sub_loader(self, tmpdir):
        structure = {
            "file.yml": {"include": ["inc.yml"]},
            "inc.yml": {"key": "value"}
        }
        with file_structure(structure, tmpdir):
            loader = CompositeLoader(FancyDict, include_key="include")
            result = {"key": "value"}
            assert result == loader.load("file.yml")


class TestKeyAnnotationsConverter:
    def test_key_name_and_defaults(self):
        annotations = KeyAnnotationsConverter.decode(key="key")["annotations"]
        assert not annotations.finalized
        assert annotations.get("condition") is None
        assert annotations.get("merge_method") is None

    def test_finalized(self):
        annotations = KeyAnnotationsConverter.decode(key="(k)")["annotations"]
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
