class Groupby:
    def __init__(self, operation, base_data=0):
        self.grouped_data = {}
        self.operation = operation
        self.base_data = base_data

    def add_data(self, id_client, group_key, group_value):
        if not (id_client, group_key) in self.grouped_data:
            self.grouped_data[id_client, group_key] = self.base_data

        self.grouped_data[id_client, group_key] = self.operation(
            self.grouped_data[id_client, group_key], group_value
        )

    def delete_client(self, id_client):
        keys_to_delete = [
            key for key in self.grouped_data.keys() if key[0] == id_client
        ]
        for key in keys_to_delete:
            del self.grouped_data[key]
