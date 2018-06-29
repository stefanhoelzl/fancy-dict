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


class NoLoaderForSourceAvailable(FancyDictException):
    """Exception when no Loader can load from the given source"""
    def __init__(self, source):
        super().__init__("Cannot load from source ({})".format(source))
        self.source = source
