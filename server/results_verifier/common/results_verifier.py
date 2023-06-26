import socket, signal, sys, threading, queue
from common.results_sender import ResultsSender
from server.common.queue.connection import Connection
from server.common.utils_messages_client import results_message, last_message
from server.common.utils_messages_eof import ack_msg, get_id_client
from server.common.utils_messages_group import decode, is_eof
from server.common.utils_messages_results import decode_request_results, error_message
from server.common.keep_alive.keep_alive import KeepAlive


class ResultsVerifier:
    CHUNK_SIZE = 100

    def __init__(
        self,
        address_consult_clients,
        name_recv_queue,
        name_em_queue,
        name_session_manager_queue,
        name_send_exchange,
        name_send_queue,
        amount_queries,
    ):
        self.__init_results_verifier(
            address_consult_clients,
            name_session_manager_queue,
            name_recv_queue,
            name_send_exchange,
            name_send_queue,
            amount_queries,
        )
        self.__connect(
            name_recv_queue,
            name_em_queue,
            name_send_exchange,
            name_send_queue,
            amount_queries,
        )

    def __init_results_verifier(
        self,
        address_consult_clients,
        name_session_manager_queue,
        name_recv_queue,
        name_send_exchange,
        name_send_queue,
        amount_queries,
    ):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.ids_clients = set()
        self.queries_results = {}
        self.queries_ended = {}
        self.amount_queries = amount_queries

        self.client_handlers_queues = [queue.Queue() for i in range(3)]
        self.sender = ResultsSender(
            name_session_manager_queue,
            name_recv_queue,
            address_consult_clients,
            self.client_handlers_queues
        )
        self.keep_alive = KeepAlive()
        print("action: results_verifier_started | result: success")

    def __connect(
        self,
        name_recv_queue,
        name_em_queue,
        name_send_exchange,
        name_send_queue,
        amount_queries,
    ):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.routing_queue(
                name_recv_queue,
                routing_keys=[str(i) for i in range(1, amount_queries + 1)]+['request_results'],
            )

            self.em_queue = self.queue_connection.pubsub_queue(name_em_queue)
            self.send_queue = self.queue_connection.routing_building_queue(
                name_send_exchange, name_send_queue
            )
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def run(self):
        """
        start receiving messages.
        """
        self.keep_alive.start()
        self.sender.start()
        self.recv_queue.receive(self.process_messages)
        try:
            self.queue_connection.start_receiving()
        except:
            if self.running:
                raise  # gracefull quit

        self.sender.join()
        self.keep_alive.stop()
        self.keep_alive.join()

    def process_messages(self, body, id_query):
        if id_query == 'request_results':
            id_client_handler, id_client = decode_request_results(body)
            if self.__verify_last_result(id_client):
                self.__inform_results(id_client_handler, id_client)
            else:
                self.__inform_error(id_client_handler)
        else:
            id_query = int(id_query)
            if is_eof(body):
                print("action: eof_trips_arrived")
                self.__eof_arrived(id_query, body)
            else:
                self.__query_result_arrived(body, id_query)

    def __query_result_arrived(self, body, id_query):
        """
        stores the results by query.
        """
        header, results = decode(body)
        id_client = header.id_client
        self.__verify_client(id_client)
        self.queries_results[id_client, id_query] += results

    def __add_client(self, id_client):
        print(f"action: add_client | result: success | id_client: {id_client}")
        self.ids_clients.add(id_client)

        for id_query in range(1, self.amount_queries + 1):
            self.queries_ended[id_client, id_query] = False
            self.queries_results[id_client, id_query] = []

    def __eof_arrived(self, id_query, body):
        """
        save the finished query and send an acknowledgment to the EOF manager.
        then, check if all the queries have ended or if it needs to continue waiting for the EOF, otherwise.
        """
        id_client = get_id_client(body)
        self.__verify_client(id_client)
        self.em_queue.send(ack_msg(body))
        self.queries_ended[id_client, id_query] = True

        self.__verify_last_result(id_client)

    def __verify_client(self, id_client):
        if id_client not in self.ids_clients:
            self.__add_client(id_client)

    def __verify_last_result(self, id_client):
        """
        check if all the queries have ended or if it needs to continue waiting for the EOF, otherwise.
        if it finishes, report the results to the client.
        """
        ended = True
        for query in self.queries_ended:
            if query[0] == id_client:
                if not self.queries_ended[query]:
                    ended = False

        return ended

    def __inform_results(self, id_client_handler, id_client):
        queue = self.client_handlers_queues[id_client_handler]

        batches_to_send = self.__get_batches_to_send(id_client)
        queue.put(batches_to_send)

        print(f"action: inform_results | result: success | id_client: {id_client}")

    def __inform_error(self, id_client_handler):
        queue = self.client_handlers_queues[id_client_handler]
        queue.put(error_message())
        print(f"action: inform_results | result: failure")

    def __get_batches_to_send(self, id_client):
        results_client = self.__get_results_client(id_client)
        batches_to_send = []
        id_batch = 0

        for id_query, results_query in enumerate(results_client, start=1):
            for result in results_query:
                batch = results_message(id_query, id_batch, result)
                batches_to_send.append(batch)
                id_batch += 1

        return batches_to_send

    def __get_results_client(self, id_client):
        results_client = []
        for key, results_query in self.queries_results.items():
            if id_client == key[0]:
                results_client.append(self.__partition_into_batches(results_query))

        return results_client

    def __partition_into_batches(self, list_batch):
        batches = []
        last = 0
        for i, elem in enumerate(list_batch):
            if (i + 1) % self.CHUNK_SIZE == 0 or i + 1 == len(list_batch):
                batches.append(list_batch[last : i + 1])
                last = i + 1

        return batches

    def __delete_client(self, id_client):
        self.__delete_from_dict(self.queries_ended, id_client)
        self.__delete_from_dict(self.queries_results, id_client)
        self.ids_clients.discard(id_client)
        print(f"action: delete_client | result: success | id_client: {id_client}")

    def __delete_from_dict(self, dict_clients, id_client):
        keys_to_delete = [key for key in dict_clients.keys() if key[0] == id_client]
        for key in keys_to_delete:
            del dict_clients[key]

    def stop(self, *args):
        if self.running:
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )

            self.running = False
