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


class FileNotFoundInBaseDirs(FancyDictException):
    """Exception when no file to load was found"""
    def __init__(self, file_name, base_dirs):
        super().__init__("File {} not found in {}".format(
            file_name, ", ".join((str(p) for p in base_dirs))
        ))
        self.file_name = file_name
        self.base_dirs = base_dirs
