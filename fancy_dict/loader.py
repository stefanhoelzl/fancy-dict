"""Loader and Dumper to serialize FancyDicts"""
import re
from pathlib import Path

import yaml

from fancy_dict.errors import FileNotFoundInBaseDirs
from fancy_dict import merger, conditions
from fancy_dict import fancy_dict


class LoaderBase:
    def __init__(self, output_type=None, **kwargs):
        self.output_type = output_type if output_type else fancy_dict.FancyDict

    def load(self, item):
        raise NotImplementedError()


class DictLoader(LoaderBase):
    def load(self, dct):
        loaded_dict = self.output_type()
        for k, v in dct.items():
            loaded_dict[k] = v
        return loaded_dict


class FileLoader(DictLoader):
    """Loads a FancyDict

    Looks up files in given base directoies.
    Supports a special include key to include other files.
    """

    def __init__(self, base_dirs=('.',), include_key="include", ):
        super().__init__()
        self._base_dirs = base_dirs
        self._include_key = include_key

    def load(self, dict_file):
        """Loads a yaml/json file as FancyDict

        Args:
            dict_file: filename

        Returns:
            FancyDict
        """
        full_path = self._find_filepath(dict_file)
        base_dict = self.output_type()
        with open(full_path, "r") as yml_file:
            fancy_dict = self.output_type(yaml.load(yml_file))
        for include in fancy_dict.pop(self._include_key, ()):
            base_dict.update(self.load(include))
        base_dict.update(fancy_dict)
        return base_dict

    def _find_filepath(self, filename):
        for base_dir in self._base_dirs:
            full_path = Path(Path(base_dir) / Path(filename))
            if full_path.exists():
                return full_path
        raise FileNotFoundInBaseDirs(filename, self._base_dirs)


class Loader(DictLoader):
    pass


class AnnotationsSerializer:
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
    def from_string(cls, annotated_key):
        """Parses an annotations string

        Args:
            annotated_key: an annotated key string

        Returns:
            AnnotationsParser
        """
        return fancy_dict.Annotations(
            merge_method=cls._parse_merge_method(annotated_key),
            condition=cls._parse_condition(annotated_key),
            finalized=cls._parse_finalized(annotated_key),
        )

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
    def to_string(cls, annotation):
        annotated_key = ""
        if annotation.condition:
            reversed_conditions = {v: k for k, v in cls.CONDITIONS.items()}
            condition = reversed_conditions[annotation.condition]
            annotated_key += condition
        if annotation.finalized:
            annotated_key += "({})"
        else:
            annotated_key += "{}"
        if annotation.merge_method:
            reversed_merge_methods \
                = {v: k for k, v in cls.MERGE_METHODS.items()}
            method_name = reversed_merge_methods[annotation.merge_method]
            annotated_key += "[{}]".format(method_name)
        return annotated_key
