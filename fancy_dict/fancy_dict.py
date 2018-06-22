class FancyDict(dict):
    def __setitem__(self, key, value):
        if isinstance(value, dict):
            super().__setitem__(key, FancyDict(value))
        else:
            super().__setitem__(key, value)

    def _update_value(self, key, value):
        if isinstance(self.get(key), dict) and isinstance(value, dict):
            self[key].update(value)
        else:
            self[key] = value

    def _update_from_dict(self, dct):
        for k, v in dct.items():
            self._update_value(k, v)

    def update(self, dct=None, **kwargs):
        if dct is not None:
            self._update_from_dict(dct)
        if kwargs:
            self.update(kwargs)
