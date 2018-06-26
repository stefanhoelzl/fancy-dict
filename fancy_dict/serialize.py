"""Loader and Dumper to serialize FancyDicts"""

from pathlib import Path

import yaml

from fancy_dict import FancyDict
from fancy_dict.errors import FileNotFoundInBaseDirs


class Loader:
    """Loads a FancyDict

    Looks up files in given base directoies and supports include keys
    """
    @staticmethod
    def default_dict_type():
        """Default dict type

        Can be overwritten to customize Loader behavior.

        Returns:
            type
        """
        return FancyDict

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
        dict_type = self.default_dict_type()
        base_dict = dict_type()
        with open(full_path, "r") as yml_file:
            fancy_dict = dict_type(yaml.load(yml_file))
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
