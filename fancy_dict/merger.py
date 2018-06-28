"""Default merging methods for FancyDict"""


class MergeMethod:
    """Wrapper for a merging method

    Can check if the method can merge two values.
    Provides a method to merge to values.

    Method applies when the old value is an instance of from_types
    and the new value is an instance of to_types.
    """
    def __init__(self, method, from_types=None, to_types=None):
        self._method = method
        self._from_types = from_types
        self._to_types = to_types

    def __call__(self, old_value, new_value):
        """Merges an old with an new value.

        Args:
            old_value: old value to merge
            new_value: new vlaue to merge
        Returns:
            merged value
        """
        return self._method(old_value, new_value)

    def applies(self, old, new):
        """Checks if the types of old and new match from_types and to_types

        Args:
            old: old value to merge
            new: new value to merge

        Returns:
            True if old of type from_types and new of type to_types.
        """
        if self._from_types is None or isinstance(old, self._from_types):
            if self._to_types is None or isinstance(new, self._to_types):
                return True
        return False


def overwrite(_old, new):
    """Overwrites the old value with the new value

    Args:
        _old: old value to be overwritten
        new: new value to overwrite

    Returns:
        new value
    """
    return new


def update(old, new):
    """Updates the old value with the new value

    Args:
        old: old value to update
        new: new value with updates

    Returns:
        updated old value
    """
    old.update(new)
    return old


def add(old, new):
    """Adds the new value to the old value

    Args:
        old: old value to extend
        new: new value

    Returns:
        extended old value
    """
    return old + new
