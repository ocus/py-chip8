class Input(object):
    def __init__(self):
        self.key_code = None

    def read(self):
        return self.key_code

    def press(self, key_code):
        self._ensure_key_code(key_code)
        self.key_code = key_code

    def unpress(self):
        self.press(None)

    @staticmethod
    def _ensure_key_code(key_code):
        if key_code is not None and key_code < 0x0 or key_code > 0xf:
            raise IndexError('KeyCode %s is not valid' % hex(key_code))
