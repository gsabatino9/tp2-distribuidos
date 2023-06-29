class JoinData:
    def __init__(self, pk_indexes: tuple, len_msg: int, backing_storage=None):
        self.data = {}
        self.pk_indexes = pk_indexes
        self.len_msg = len_msg
        self.backing_storage = backing_storage
        if self.backing_storage:
            self.__try_recover_state()

    def __try_recover_state(self):
        for _, entry in self.backing_storage.items():
            self.add_data(entry)

    def add_data(self, entry):
        key = tuple(entry[index] for index in self.pk_indexes)
        value = [
            field
            for i, field in enumerate(entry[: self.len_msg])
            if i not in self.pk_indexes
        ]
        self.data[key] = value
        if self.backing_storage:
            self.backing_storage.set(f"{key}", entry)

    def find_record(self, key):
        if key in self.data:
            return self.data.get(key)
