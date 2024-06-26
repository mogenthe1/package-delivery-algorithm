class HashTable:
    def __init__(self, size=10):
        self.size = size
        self.table = [[] for _ in range(size)]

    def _hash(self, key):
        return key % self.size

    def insert(self, key, value):
        hash_index = self._hash(key)
        for i, (k, v) in enumerate(self.table[hash_index]):
            if k == key:
                self.table[hash_index][i] = (key, value)
                return
        self.table[hash_index].append((key, value))

    def lookup(self, key):
        hash_index = self._hash(key)
        for k, v in self.table[hash_index]:
            if k == key:
                return v
        return None
