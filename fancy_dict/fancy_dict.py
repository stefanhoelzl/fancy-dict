"""Dictionary extended load/update/filter features.

Loads data from different sources using Loaders.
Updates data with customizeable MergeMethods.
Queries data using Transformations.
"""
from . import merger
from .errors import NoMergeMethodApplies
from .loader import CompositeLoader
from .annotations import Annotations


class FancyDict(dict):
    """Extends dict by merge methods, filter and load functionality.

    Merging methods can define custom behavior how to merge certain values
    in the dict.

    Conditions can prevent merging a value under certain circumstances.

    Keys can be marked as finalizedd to avoid future updates.

    Queries allow it to retrieve values deep inside the dict.

    Loader allow it to load data from various sources.
    """
    __slots__ = ["_annotations"]
    MERGE_METHODS = (
        merger.MergeMethod(merger.update,
                           from_types=dict, to_types=dict),
        merger.MergeMethod(merger.overwrite),
    )

    @classmethod
    def load(cls, source, annotations_decoder=None,
             loader=CompositeLoader, **loader_kwargs):
        """Loads FancyDicts from different sources.

        Args:
            source: Source specifier
            annotations_decoder: Decoder used for annotations
            loader: Loader class used to load from the given source
            **loader_kwargs: Arguments for the Loader
        Returns:
            FancyDict with initialized data from given source
        """
        if isinstance(source, FancyDict):
            return source
        return loader(cls, **loader_kwargs).load(
            source, annotations_decoder=annotations_decoder
        )

    def __new__(cls, *args, **kwargs):
        if args and isinstance(args[0], list):
            return [FancyDict(item) for item in args[0]]
        return super().__new__(cls, *args, **kwargs)

    def __init__(self, __dct=None, **kwargs):
        super().__init__()
        self._annotations = {}
        self.update(__dct, **kwargs)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = self.load(value)
        super().__setitem__(key, value)

    def __setattr__(self, key, value):
        if hasattr(type(self), key) or key in FancyDict.__slots__:
            super().__setattr__(key, value)
        else:
            self[key] = value

    def __getattr__(self, item):
        if item not in self:
            self[item] = type(self)()
        return self[item]

    def annotate(self, key, annotations=None, **kwargs):
        """Adds Annotations for specific key.

        Args:
            key: name of the key
            annotations: Annotations object with the annotions to add
            **kwargs: arguments used to create an Annotations (optional)

        Returns:

        """
        if annotations or kwargs:
            annotations = Annotations(**kwargs) if annotations is None \
                else annotations
            if key in self._annotations:
                self._annotations[key].update(annotations)
            else:
                self._annotations[key] = annotations

    def get_annotations(self, key, default=None):
        """Gets the Annotations for a key.

        A default value is returned if no annotations are set for the key.

        Args:
            key: name of the key.
            default: return value if no annotations for this key specified.

        Returns:
            Annotations for this key or default.
        """
        return self._annotations.get(key, default)

    def filter(self, filter_method, recursive=False, flat=False):
        """Returns a filtered FancyDict

        filter_method must be a method with two parameters.
        filter_method returns True or False for a given pair of key/value.
        If filter_method returns True,
        the key/value pair is added to the filtered dict.

        Args:
            filter_method: determines if key/value pair gets into return
            recursive: searches recursive into sub dicts
            flat: if recursive, flattens the result

        Returns:
            FancyDict with filtered content
        """
        result = FancyDict()
        for key, value in self.items():
            if isinstance(value, FancyDict) and recursive:
                if flat:
                    result.update(value.filter(filter_method,
                                               recursive=True, flat=True))
                else:
                    result[key] = value.filter(filter_method, recursive=True)
            elif filter_method(key, value):
                result[key] = value
        return result

    def update(self, __dct=None, **kwargs):
        """Updates the data using MergeMethods and Annotations

        When updating with a plain dict, they get first converted to FancyDicts

        First key specific annotations get evaluated for each key
        to check if and how the value for this key can be updated.

        They are evaluated in the following order.
        1. When a key is finalized, the value never gets updated.
        2. The condition annotation based on old and new value gets evaluated
            * the condition of the destination is used
            * if there is none, the condition of the source is used
            * if there is none, the default condition is used
            * if the condition is false, the value gets not updated

        If the value can be updated, the merge method is looked up the
        in the following order:
        1. merge method annotated in source
        2. merge method annotated in destination
        3. global merge methods
            * first the source merge methods are evaluated
            * second the destination merge methods are evaluated
            * the first merge method which applies to the old and new value
              is used.

        Args:
            __dct: source dict to merge into destination (self)
            **kwargs: key-value-pairs for source dict
        Raises:
            NoMergeMethodApplies if no valid MergeStrategy was found.
        """
        if isinstance(__dct, dict):
            self._update_with_fancy_dict(self.load(__dct))
        if kwargs:
            self._update_with_fancy_dict(self.load(kwargs))

    def _update_with_fancy_dict(self, fancy_dict):
        for key in fancy_dict:
            self._update_value(key, fancy_dict)

    def _update_value(self, key, from_dict):
        if self.get_annotations(key, Annotations()).finalized:
            return

        old_value = self.get(key)
        new_value = from_dict.get(key)
        self.annotate(key, from_dict.get_annotations(key))
        annotations = self.get_annotations(key, Annotations())
        if annotations.condition(old_value, new_value):
            if annotations.get("merge_method") is not None:
                self[key] = annotations.merge_method(old_value, new_value)
            else:
                methods = from_dict.MERGE_METHODS + self.MERGE_METHODS
                for method in methods:
                    if method.applies(old_value, new_value):
                        self[key] = method(old_value, new_value)
                        break
                else:
                    raise NoMergeMethodApplies(old_value, new_value)
