from server.common.duplicate_filter import DuplicateFilter


class ResultsVerifierState:
    def __init__(self, amount_queries):
        self.ids_clients = set()
        self.queries_results = {}
        self.queries_ended = {}
        self.amount_queries = amount_queries

    def add_client(self, id_client):
        if id_client not in self.ids_clients:
            self.__add_client(id_client)
            return True

        return False

    def add_results(self, id_client, id_query, results):
        self.queries_results[id_client, id_query] += results

    def get_results(self, id_client):
        return map(
            lambda e: e[1],
            filter(lambda e: e[0][0] == id_client, self.queries_results.items()),
        )

    def verify_last_result(self, id_client):
        ended = True
        for query in self.queries_ended:
            if query[0] == id_client:
                if not self.queries_ended[query]:
                    ended = False

        return ended

    def mark_query_as_ended(self, id_client, id_query):
        self.queries_ended[id_client, id_query] = True

    def delete_client(self, id_client):
        self.__delete_from_dict(self.queries_ended, id_client)
        self.__delete_from_dict(self.queries_results, id_client)
        self.ids_clients.discard(id_client)

    def write_checkpoints(self):
        pass  # Not impld yet

    def __add_client(self, id_client):
        self.ids_clients.add(id_client)

        for id_query in range(1, self.amount_queries + 1):
            self.queries_ended[id_client, id_query] = False
            self.queries_results[id_client, id_query] = []

    def __delete_from_dict(self, dict_clients, id_client):
        keys_to_delete = [key for key in dict_clients.keys() if key[0] == id_client]
        for key in keys_to_delete:
            del dict_clients[key]


class ClientState:
    def __init__(self):
        self.results = {}
        self.dup_filter = DuplicateFilter()
