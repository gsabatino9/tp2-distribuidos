from server.common.atomic_storage.atomic_storage import AtomicBucket


class SessionManagerState:
    def __init__(self):
        self.active_clients = {}
        self.bucket = AtomicBucket("session-manager")
        self.__try_recover_state()

    def __try_recover_state(self):
        self.active_clients = {
            address: id_client for address, id_client in self.bucket.items()
        }

    def add_client(self, address, id_client):
        address = str(address, encoding="utf-8")
        self.active_clients[address] = id_client
        self.bucket.set(address, id_client)

    def get_client(self, address):
        address = str(address, encoding="utf-8")
        return self.active_clients.get(address, None)

    def delete_client(self, address):
        address = str(address, encoding="utf-8")
        self.bucket.discard(address)
        return self.active_clients.pop(address, None)

    def clients_count(self):
        return len(self.active_clients)

    def write_checkpoint(self):
        self.bucket.write_checkpoint()
