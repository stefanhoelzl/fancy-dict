def always(old_value, new_value):
    return True


def if_existing(old_value, new_value):
    if old_value is not None:
        return True
    return False


def if_not_existing(old_value, new_value):
    return not if_existing(old_value, new_value)
