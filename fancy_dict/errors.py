"""FancyDict Exceptions"""


class FancyDictException(Exception):
    """Base Exception for FancyDict errors"""
    pass


class NoValidMergeStrategyFound(FancyDictException):
    """Exception when no merge strategy was found"""
    def __init__(self, key, old_value, new_value):
        super().__init__("Cannot merge {} with {} for key '{}'".format(
            new_value, old_value, key
        ))
        self.key = key
        self.old_value = old_value
        self.new_value = new_value
