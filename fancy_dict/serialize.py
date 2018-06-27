"""Loader and Dumper to serialize FancyDicts"""

import re
from pathlib import Path

import yaml

from fancy_dict import FancyDict, merger, conditions
from fancy_dict.errors import FileNotFoundInBaseDirs


class Annotation:
    """Annotation for a FancyDict key

    Composed of a merge strategy, a merge condition and if the key is locked.

    Implements method to serialize and deserialize Annotations
    """
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
        """Parses an annotation string

        Args:
            annotated_key: an annotated key string

        Returns:
            AnnotationParser
        """
        return AnnotationParser(annotated_key)

    def __init__(self, key, merge_method=None, condition=None, locked=False):
        self.key = key
        self.strategy = merger.MergeStrategy(merge_method, key=key) \
            if merge_method else None
        self.condition = condition
        self.locked = locked

    def __str__(self):
        annotated_key = ""
        if self.condition:
            reversed_conditions = {v: k for k, v in self.CONDITIONS.items()}
            condition = reversed_conditions[self.condition]
            annotated_key += condition
        if self.locked:
            annotated_key += "({})".format(self.key)
        else:
            annotated_key += self.key
        if self.strategy:
            reversed_merge_methods \
                = {v: k for k, v in self.MERGE_METHODS.items()}
            method_name = reversed_merge_methods[self.strategy.method]
            annotated_key += "[{}]".format(method_name)
        return annotated_key


class AnnotationParser(Annotation):
    """Deserializes an Annotation string"""
    def __init__(self, annotated_key):
        super().__init__(
            self._parse_key(annotated_key),
            merge_method=self._parse_merge_method(annotated_key),
            condition=self._parse_condition(annotated_key),
            locked=self._parse_locked(annotated_key),
        )

    @classmethod
    def _parse_locked(cls, annotated_key):
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


class Loader:
    """Loads a FancyDict

    Looks up files in given base directoies.
    Supports a special include key to include other files.
    """
    DICT_TYPE = FancyDict

    def __init__(self, base_dirs=('.',), include_key="include"):
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
        base_dict = self.DICT_TYPE()
        with open(full_path, "r") as yml_file:
            fancy_dict = self.DICT_TYPE(yaml.load(yml_file))
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
