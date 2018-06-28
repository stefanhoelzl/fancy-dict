"""Loader and Dumper to serialize FancyDicts"""
import re
from pathlib import Path
from collections import namedtuple

import yaml

from fancy_dict.errors import FileNotFoundInBaseDirs
from fancy_dict import merger, conditions
from fancy_dict import fancy_dict


KeyValue = namedtuple("KeyValue", "key value")


class AnnotationsDecoder:
    @classmethod
    def decode(cls, key=None, value=None):
        raise NotImplementedError()


class AnnotationsEncoder:
    @classmethod
    def encode(cls, annotation, key=None, value=None):
        raise NotImplementedError()


class KeyAnnotationsConverter(AnnotationsEncoder):
    """Deserializes an Annotations string"""
    MERGE_METHODS = {
        "add": merger.add,
        "overwrite": merger.overwrite,
        "update": merger.update,
    }

    CONDITIONS = {
        "#": conditions.always,
        "?": conditions.if_existing,
        "+": conditions.if_not_existing,
    }

    @classmethod
    def decode(cls, key=None, value=None):
        annotations = fancy_dict.Annotations(
            merge_method=cls._parse_merge_method(key),
            condition=cls._parse_condition(key),
            finalized=cls._parse_finalized(key),
        )
        key = cls._parse_key(key)
        return {
            "key": key,
            "value": value,
            "annotations": annotations
        }

    @classmethod
    def _parse_finalized(cls, annotated_key):
        key = cls._parse_key(annotated_key)
        locking_pattern = r"\({key}\)".format(key=key)
        match = re.search(locking_pattern, annotated_key)
        return bool(match)

    @classmethod
    def _parse_key(cls, annotated_key):
        condition_marker = "".join(cls.CONDITIONS.keys())
        key_pattern = r"^[{}]?\({{0,1}}(?P<key>[^)[]+)\){{0,1}}".format(
            condition_marker
        )
        return re.match(key_pattern, annotated_key).group("key")

    @classmethod
    def _parse_merge_method(cls, annotated_key):
        strategy_pattern = r"\[(?P<name>.+)\]$"
        match = re.search(strategy_pattern, annotated_key)
        if match:
            return cls.MERGE_METHODS[match.group("name")]
        return None

    @classmethod
    def _parse_condition(cls, annotated_key):
        for marker, condition in cls.CONDITIONS.items():
            if marker in annotated_key:
                return condition
        return None

    @classmethod
    def encode(cls, annotation, key=None, value=None):
        return {
            "key": cls.to_string(annotation).format(key),
            "value": value
        }

    @classmethod
    def to_string(cls, annotation):
        annotated_key = ""
        if annotation.get("condition"):
            reversed_conditions = {v: k for k, v in cls.CONDITIONS.items()}
            condition = reversed_conditions[annotation.condition]
            annotated_key += condition
        if annotation.get("finalized"):
            annotated_key += "({})"
        else:
            annotated_key += "{}"
        if annotation.get("merge_method"):
            reversed_merge_methods \
                = {v: k for k, v in cls.MERGE_METHODS.items()}
            method_name = reversed_merge_methods[annotation.merge_method]
            annotated_key += "[{}]".format(method_name)
        return annotated_key


class LoaderBase:
    def __init__(self, output_type=None, **kwargs):
        self.type = output_type if output_type else fancy_dict.FancyDict

    def load(self, item, annotations_decoder=None):
        raise NotImplementedError()


class DictLoader(LoaderBase):
    def load(self, item, annotations_decoder=None):
        return self.type(
            self._load_without_running_annotations(item, annotations_decoder)
        )

    def _load_without_running_annotations(self, dct, annotations_decoder=None):
        loaded_dict = self.type()
        for key, value in dct.items():
            if annotations_decoder:
                key, value = self._annotate(loaded_dict, key, value,
                                            annotations_decoder)
            if isinstance(value, dict):
                value = DictLoader._load_without_running_annotations(
                    self, value, annotations_decoder=annotations_decoder
                )
            loaded_dict[key] = value
        return loaded_dict

    @staticmethod
    def _annotate(dct, key, value, annotations_decoder):
        decoded = annotations_decoder.decode(key=key, value=value)
        key = decoded["key"]
        value = decoded["value"]
        dct.annotate(key, decoded["annotations"])
        return key, value


class FileLoader(DictLoader):
    """Loads a FancyDict

    Looks up files in given base directoies.
    Supports a special include key to include other files.
    """

    def __init__(self, base_dirs=('.',), include_key="include",
                 output_type=None):
        super().__init__(output_type)
        self._base_dirs = base_dirs
        self._include_key = include_key

    def load(self, item, annotations_decoder=KeyAnnotationsConverter):
        """Loads a yaml/json file as FancyDict

        Args:
            dict_file: filename

        Returns:
            FancyDict
        """
        full_path = self._find_filepath(item)
        dct = self._load_dict(full_path, annotations_decoder)
        base_dict = self._build_base_dict_with_includes(
            dct.pop(self._include_key, ()), annotations_decoder
        )
        base_dict.update(dct)
        return base_dict

    def _find_filepath(self, filename):
        for base_dir in self._base_dirs:
            full_path = Path(Path(base_dir) / Path(filename))
            if full_path.exists():
                return full_path
        raise FileNotFoundInBaseDirs(filename, self._base_dirs)

    def _load_dict(self, full_path, annotations_decoder):
        with open(full_path, "r") as yml_file:
            return super()._load_without_running_annotations(
                yaml.load(yml_file),
                annotations_decoder=annotations_decoder
            )

    def _build_base_dict_with_includes(self, includes, annotations_decoder):
        base_dict = self.type()
        for include in includes:
            base_dict.update(
                self.load(include, annotations_decoder=annotations_decoder)
            )
        return base_dict


class Loader(DictLoader):
    pass
