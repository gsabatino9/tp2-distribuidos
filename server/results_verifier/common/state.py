from server.common.duplicate_filter import DuplicateFilter
from server.common.atomic_storage.atomic_storage import AtomicBucket


class ResultsVerifierState:
    def __init__(self, amount_queries):
        self.amount_queries = amount_queries
        self.clients = {}

    def __get_client(self, id_client):
        if id_client not in self.clients:
            self.clients[id_client] = ClientState(AtomicBucket(id_client))

        return self.clients[id_client]

    def add_client(self, id_client):
        if id_client not in self.clients:
            self.__get_client(id_client)  # create it
            return True

        return False

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

    def mark_batch_as_processed(self, id_client, id_query, id_batch):
        self.__get_client(id_client).mark_batch_as_processed(id_query, id_batch)

    def has_batch_been_processed(self, id_client, id_query, id_batch):
        return self.__get_client(id_client).has_batch_been_processed(id_query, id_batch)

    def delete_client(self, id_client):
        if client := self.clients.pop(id_client, None):
            client.drop()

    def write_checkpoints(self):
        for client in self.clients.values():
            client.write_checkpoint()


class ClientState:
    def __init__(self, bucket: AtomicBucket):
        self.results = {}
        self.finished_queries = set()

        self.results_bucket = bucket.collection("results")
        self.finished_queries_bucket = bucket.collection("finished_queries")
        self.dup_filter = {}
        # TODO: ponerle 5 := amount_queries+1
        for id_query in range(1, 5):
            self.dup_filter[id_query] = DuplicateFilter(
                bucket.collection(f"dup_filter#{id_query}")
            )

        self.bucket = bucket
        self.was_modified = False

        self.__try_recover_state()

    def __try_recover_state(self):
        for id_query, results in self.results_bucket.items():
            self.results[int(id_query)] = results

        for id_query, _ in self.finished_queries_bucket.items():
            self.finished_queries.add(int(id_query))

    def add_results(self, id_query, results):
        if id_query not in self.results:
            self.results[id_query] = []

        self.was_modified = True
        self.results[id_query].extend(results)
        self.results_bucket.set(id_query, self.results[id_query])

    def mark_query_as_finished(self, id_query):
        self.was_modified = True
        self.finished_queries.add(id_query)
        self.finished_queries_bucket.set(id_query, 1)

    def mark_batch_as_processed(self, id_query, id_batch):
        self.was_modified = True
        self.dup_filter[id_query].mark_as_seen(id_batch)

    def get_results(self):
        return self.results.items()

    def count_finished_queries(self):
        return len(self.finished_queries)

    def has_batch_been_processed(self, id_query, id_batch):
        return self.dup_filter[id_query].has_been_seen(id_batch)

    def write_checkpoint(self):
        if self.was_modified:
            self.bucket.write_checkpoint()
            self.was_modified = False

    def drop(self):
        self.bucket.drop()
