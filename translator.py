from hashlib import sha3_512

class TranslationEntity:
    def __init__(self, original, langFrom, langTo, translated=None) -> None:
        self._original = original 
        self._translated = translated
        self._langFrom = langFrom
        self._langTo = langTo
        self._hash = self._calc_hash()

    def _calc_hash(self):
        if self.original is not None:
            hash_object = sha3_512()
            hash_object.update(self.original.encode('utf-8'))  # Calculating for original 
            return hash_object.hexdigest()
        else:
            raise ValueError(f"Cannot calculate hash for {self.original} value.")

    @property
    def hash(self):
        return self._hash
    
    @property
    def original(self):
        return self._original
    
    @property
    def translated(self):
        return self._translated
    
    @property
    def langFrom(self):
        return self._langFrom
    
    @property
    def langTo(self):
        return self._langTo
    
    @translated.setter
    def translated(self, value):
        self._translated = value

    @original.setter
    def original(self, value):
        self._original = value
        self._hash = self._calc_hash(value)

    @hash.setter
    def hash(self, value):
        raise AttributeError("A hash cannot be directly set")