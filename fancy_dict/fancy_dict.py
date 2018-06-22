class FancyDict(dict):
    def __init__(self, __dct=None, **kwargs):
        super().__init__()
        self.update(__dct)
        self.update(kwargs)

    def __setitem__(self, key, value):
        if isinstance(value, dict):
            value = FancyDict(value)
        super().__setitem__(key, value)

    def _update_value(self, key, value):
        if isinstance(self.get(key), dict) and isinstance(value, dict):
            self[key].update(value)
        else:
            self[key] = value

    def _update_with_dict(self, dct):
        for k, v in dct.items():
            self._update_value(k, v)

    def update(self, __dct=None, **kwargs):
        if isinstance(__dct, dict):
            self._update_with_dict(__dct)
        self._update_with_dict(kwargs)
