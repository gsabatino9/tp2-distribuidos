from server.common.duplicate_filter import DuplicateFilter


class ResultsVerifierState:
    def __init__(self, amount_queries):
        self.amount_queries = amount_queries
        self.clients = {}

    def __get_client(self, id_client):
        if id_client not in self.clients:
            self.clients[id_client] = ClientState()

        return self.clients[id_client]

    def add_client(self, id_client):
        return id_client not in self.clients

    def add_results(self, id_client, id_query, results):
        self.__get_client(id_client).add_results(id_query, results)

    def get_results(self, id_client):
        return self.__get_client(id_client).get_results()

    def verify_last_result(self, id_client):
        return (
            self.__get_client(id_client).count_finished_queries() == self.amount_queries
        )

    def mark_query_as_ended(self, id_client, id_query):
        self.__get_client(id_client).mark_query_as_finished(id_query)

    def delete_client(self, id_client):
        self.clients.pop(id_client, None)

    def write_checkpoints(self):
        pass  # Not impld yet


class ClientState:
    def __init__(self):
        self.results = {}
        self.finished_queries = set()
        self.dup_filter = DuplicateFilter()

    def add_results(self, id_query, results):
        if id_query not in self.results:
            self.results[id_query] = []

        self.results[id_query].extend(results)

    def get_results(self):
        return self.results.items()

    def count_finished_queries(self):
        return len(self.finished_queries)

    def mark_query_as_finished(self, id_query):
        self.finished_queries.add(id_query)

    def mark_batch_as_processed(self, id_batch):
        self.dup_filter.mark_as_seen(id_batch)

    def has_batch_been_processed(self, id_batch):
        return self.dup_filter.has_been_seen(id_batch)
