from server.groupby.common.client_state import ClientState


class StateManager:
    def __init__(self, operation, base_data):
        self.state_per_client = {}
        self.operation = operation
        self.base_data = base_data
        self.client_state_builder = self.__new_client_state
        self.clients_updated = set()

    def __new_client_state(self, id_client):
        return ClientState(id_client, self.operation, self.base_data)

    def __get_state(self, id_client):
        if id_client not in self.state_per_client:
            self.state_per_client[id_client] = self.client_state_builder(id_client)

        return self.state_per_client[id_client]

    def add_data(self, id_client, group_key, group_value):
        self.clients_updated.add(id_client)
        self.__get_state(id_client).groupby.add_data(group_key, group_value)

    def get_data(self, id_client, group_key):
        return self.__get_state(id_client).groupby.get_data(group_key)

    def iter_data(self, id_client):
        return iter(self.__get_state(id_client).groupby)

    def len_data(self, id_client):
        return len(self.__get_state(id_client).groupby)

    def mark_batch_as_processed(self, id_client, id_batch):
        self.clients_updated.add(id_client)
        self.__get_state(id_client).dup_filter.mark_as_seen(id_batch)

    def is_batch_already_processed(self, id_client, id_batch):
        self.clients_updated.add(id_client)
        return self.__get_state(id_client).dup_filter.has_been_seen(id_batch)

    def write_checkpoint(self, id_client):
        self.clients_updated.discard(id_client)
        self.__get_state(id_client).backing_storage.write_checkpoint()

    def write_checkpoints(self):
        """
        Write checkpoints for all clients that changed their state since the last
        checkpoint written.
        """
        clients_updated = list(self.clients_updated)
        for id_client in clients_updated:
            self.write_checkpoint(id_client)

    def delete_client(self, id_client):
        """
        Deletes a client from the state, freeing any resource associated
        with it.

        Returns True if there was a client with the given ID, False otherwise.
        """
        self.clients_updated.discard(id_client)
        if client_state := self.state_per_client.pop(id_client, None):
            client_state.drop()
            return True

        return False
