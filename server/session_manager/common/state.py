class SessionManagerState:
    def __init__(self):
        self.active_clients = {}

    def add_client(self, address, id_client):
        self.active_clients[address] = id_client

    def get_client(self, address):
        return self.active_clients.get(address, None)

    def delete_client(self, address):
        return self.active_clients.pop(address, None)

    def clients_count(self):
        return len(self.active_clients)
