from server.common.atomic_storage.atomic_storage import AtomicBucket


class JoinerState:
    def __init__(self, state_builder):
        self.clients = {}
        self.clients_updated = set()
        self.clients_storage = {}
        self.state_builder = state_builder

    def add_data(self, id_client, station):
        self.__get_client(id_client).add_data(station)
        self.clients_updated.add(id_client)

    def join_trip(self, id_client, trip):
        return self.__get_client(id_client).join_trip(trip)

    def write_checkpoints(self):
        for id_client in self.clients_updated:
            self.clients_storage[id_client].write_checkpoint()

        self.clients_updated = set()

    def delete_client(self, id_client):
        self.clients.pop(id_client, None)
        self.clients_updated.discard(id_client)
        if bucket := self.clients_storage.pop(id_client, None):
            bucket.drop()

    def __get_client(self, id_client):
        if id_client not in self.clients:
            bucket = AtomicBucket(id_client)
            self.clients[id_client] = self.state_builder(bucket)
            self.clients_storage[id_client] = bucket

        return self.clients[id_client]
