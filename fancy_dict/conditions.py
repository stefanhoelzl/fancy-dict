"""FancyDict Conditions

A condition is used by a FancyDict to prevent a value from being changed.
"""


def always(_old_value, _new_value):
    """Value can be changed always

    Args:
        _old_value: value to change
        _new_value: new value

    Returns:
        True
    """
    return True


def if_existing(old_value, _new_value):
    """Value can be changed if value already exists

    Args:
        old_value: value to change
        _new_value: new value

    Returns:
        True if old_value exists
    """
    if old_value is not None:
        return True
    return False


def if_not_existing(old_value, new_value):
    """Value can be changed if value exists not yet

    Args:
        old_value: value to change
        new_value: new value

    Returns:
        True if old_value exists not yet
    """
    return not if_existing(old_value, new_value)
