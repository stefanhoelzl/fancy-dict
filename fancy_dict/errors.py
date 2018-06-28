"""FancyDict Exceptions"""


class FancyDictException(Exception):
    """Base Exception for FancyDict errors"""
    pass


class NoMergeMethodApplies(FancyDictException):
    """Exception when no merge method applies"""
    def __init__(self, old_value, new_value):
        super().__init__("Cannot merge {} onto {}".format(
            new_value, old_value
        ))
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
