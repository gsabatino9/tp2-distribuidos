from server.common.atomic_storage.atomic_storage import AtomicBucket


class EofManagerState:
    def __init__(self, name):
        self.clients_acks = {}
        self.bucket = AtomicBucket(f"eof-manager-{name}")
        self.__try_recover_state()

    def __try_recover_state(self):
        for id_client, set_acks in self.bucket.items():
            self.clients_acks[id_client] = set_acks

    def verify_client(self, id_client):
        if id_client not in self.clients_acks:
            self.clients_acks[id_client] = []
        self.bucket.set("clients_acks", self.clients_acks)

    def add_ack_client(self, id_client, id_worker):
        if id_worker not in self.clients_acks[id_client]:
            self.clients_acks[id_client].append(id_worker)
        self.bucket.set("clients_acks", self.clients_acks)

    def amount_acks(self, id_client):
        return len(self.clients_acks[id_client])

    def delete_client(self, id_client):
        del self.clients_acks[header.id_client]
        self.bucket.set("clients_acks", self.clients_acks)

    def write_checkpoint(self):
        self.bucket.write_checkpoint()
