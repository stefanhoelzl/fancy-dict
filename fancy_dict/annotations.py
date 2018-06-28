"""Annotations for FancyDict keys"""
from .conditions import always
from .merger import overwrite


class Annotations:
    """Annotates a FancyDict key

    Composed of a merge method, a merge condition and if the key is finalized

    The merge method specifies a method
    how values for this key gets merged with other values.

    A conditions can block merging two values based on the old and new value.

    If a key is finalized, the value cannot be updated anymore.
    """
    DEFAULTS = {
        "merge_method": overwrite,
        "condition": always,
        "finalized": False
    }

    def __init__(self, **values):
        self._values = {}
        for annotation, value in values.items():
            if annotation in self.DEFAULTS:
                self._values[annotation] = value

    def get(self, key):
        """get the value of an annotation

        Returns:
            annotation value or None if not set
        """
        return self._values.get(key)

    def __getattr__(self, item):
        if item in self.DEFAULTS:
            default = self.DEFAULTS[item]
            value = self._values.get(item, default)
            return default if value is None else value
        return super().__getattribute__(item)

    def update(self, new_annotations):
        """Updates annotations.

        Updates only values which are set in the new annotations
        and keeps the other values.

        Args:
            new_annotations: Annotations with value to update
        """
        for key in self.DEFAULTS:
            if new_annotations.get(key) is not None:
                value = getattr(new_annotations, key)
                self._values[key] = value
