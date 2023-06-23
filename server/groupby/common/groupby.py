class Groupby:
    def __init__(self, operation, base_data=0, backing_storage=None):
        self.grouped_data = {}
        self.operation = operation
        self.base_data = base_data
        self.backing_storage = backing_storage
        if self.backing_storage:
            self.__try_recover_state()

    def __try_recover_state(self):
        for key, item in self.backing_storage.items():
            self.grouped_data[key] = item

    def add_data(self, group_key, group_value):
        values = self.operation(
            self.grouped_data.get(group_key, self.base_data), group_value
        )

        self.grouped_data[group_key] = values
        if self.backing_storage:
            self.backing_storage.set(group_key, values)

    def get_data(self, key):
        return self.grouped_data[key]

    def __iter__(self):
        return iter(self.grouped_data)

    def __len__(self):
        return len(self.grouped_data)
