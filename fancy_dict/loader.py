"""Loader and Dumper to serialize FancyDicts"""
import re
from pathlib import Path

import yaml

from fancy_dict.errors import FileNotFoundInBaseDirs
from fancy_dict import merger, conditions
from fancy_dict import fancy_dict


class AnnotationsDecoder:
    """Interface to decode annotations"""
    @classmethod
    def decode(cls, key=None, value=None):
        """Decodes an annotation from a key/value-pair

        Args:
            key: can be used to decode annotation
            value: can be used to decode annotation
        Returns:
            dict with the following keys:
            * key: decoded key
            * value: decoded value
            * decoded: annotation
        """
        raise NotImplementedError()


class AnnotationsEncoder:
    """Interface to encode annotations"""
    @classmethod
    def encode(cls, annotation, key=None, value=None):
        """Encodes an annotation into a key/value-pair

        Args:
            annotation: annotation to encode
            key: initial key value to encode annotation into
            value: initial value to encode annotation into
        Returns:
            dict with the following keys:
            * key: key with annotation encoded
            * value: value with annotation encoded
        """
        raise NotImplementedError()


class KeyAnnotationsConverter(AnnotationsEncoder, AnnotationsDecoder):
    """Encodes/Decodes an Annotations from the key

    The following format is used to encode and decode annotation strings:
    ?(key)[add]
    * The first character defines the condition (optional)
    * Followed by the key name
    * if the key is in round brackets, the key gets finalized (optional)
    * at the end the merge method can be specified in square brackets
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
        method_pattern = r"\[(?P<name>.+)\]$"
        match = re.search(method_pattern, annotated_key)
        if match:
            return cls.MERGE_METHODS[match.group("name")]
        return None

    @classmethod
    def _parse_condition(cls, annotated_key):
        for marker, condition in cls.CONDITIONS.items():
            if annotated_key.startswith(marker):
                return condition
        return None

    @classmethod
    def encode(cls, annotation, key=None, value=None):
        return {
            "key": cls._to_string(annotation).format(key),
            "value": value
        }

    @classmethod
    def _to_string(cls, annotation):
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


class LoaderInterface:
    """Interface for a FancyDict Loader"""
    def __init__(self, output_type=None):
        self.type = output_type if output_type else fancy_dict.FancyDict

    def load(self, source, annotations_decoder=None):
        """Loads a FancyDict from a given source

        If an annotations_decoder is given, Annotations can be decoded from
        the source data.

        Args:
            source: source to load from
            annotations_decoder: Decoder to decode annotations from source data
        Returns:
            FancyDict
        """
        raise NotImplementedError()


class DictLoader(LoaderInterface):
    """Loads a dict as FancyDict"""
    def load(self, source, annotations_decoder=None):
        return self.type(
            self._load_without_running_annotations(source, annotations_decoder)
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
    """Loads a FancyDict from a YAML/JSON file

    Looks up files in given base directoies.
    Supports a special include key to include other files.
    """

    def __init__(self, base_dirs=('.',), include_key="include",
                 output_type=None):
        super().__init__(output_type)
        self._base_dirs = base_dirs
        self._include_key = include_key

    def load(self, source, annotations_decoder=KeyAnnotationsConverter):
        """Loads a yaml/json file as FancyDict

        Args:
            source: filename

        Returns:
            FancyDict
        """
        full_path = self._find_filepath(source)
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
