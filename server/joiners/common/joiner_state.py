class JoinerState:
    def __init__(self, state_builder):
        self.clients = {}
        self.state_builder = state_builder

    def add_data(self, id_client, station):
        self.__get_client(id_client).add_data(station)

    def join_trip(self, id_client, trip):
        return self.__get_client(id_client).join_trip(trip)

    def delete_client(self, id_client):
        self.clients.pop(id_client)

    def __get_client(self, id_client):
        if id_client not in self.clients:
            self.clients[id_client] = self.state_builder(id_client)

        return self.clients[id_client]
