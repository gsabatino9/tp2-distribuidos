import socket, signal, sys
from multiprocessing import Lock
from common.clients_handler import ClientsHandler
from server.common.queue.connection import Connection
from server.common.utils_messages_eof import ack_msg, get_id_client
from server.common.utils_messages_group import decode, is_eof


class ResultsVerifier:
    def __init__(self, name_recv_queue, name_em_queue, host, port, amount_queries):
        self.__init_results_verifier(host, port, amount_queries)
        self.__connect(name_recv_queue, name_em_queue, amount_queries)

    def __init_results_verifier(self, host, port, amount_queries):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.ids_clients = set()
        self.lock = Lock()
        self.queries_results = {}
        self.queries_ended = {}
        self.amount_queries = amount_queries
        self.clients_handlers = ClientsHandler((host, port), self.lock, self.queries_ended, self.queries_results)

        print("action: results_verifier_started | result: success")

    def __connect(self, name_recv_queue, name_em_queue, amount_queries):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.routing_queue(
                name_recv_queue,
                routing_keys=[str(i) for i in range(1, amount_queries + 1)],
            )

            self.em_queue = self.queue_connection.pubsub_queue(name_em_queue)
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def run(self):
        """
        start receiving messages.
        """
        self.clients_handlers.run()
        self.recv_queue.receive(self.process_messages)
        self.queue_connection.start_receiving()

    def process_messages(self, ch, method, properties, body):
        id_query = int(method.routing_key)
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

        with self.lock:
            self.queries_results[id_client, id_query] += results

    def __add_client(self, id_client):
        print(f"action: add_client | result: success | id_client: {id_client}")
        self.ids_clients.add(id_client)
        
        self.lock.acquire()
        for id_query in range(1, self.amount_queries + 1):
            self.queries_ended[id_client, id_query] = False
            self.queries_results[id_client, id_query] = []
        self.lock.release()

    def __eof_arrived(self, id_query, body):
        """
        save the finished query and send an acknowledgment to the EOF manager.
        then, check if all the queries have ended or if it needs to continue waiting for the EOF, otherwise.
        """
        id_client = get_id_client(body)
        self.__verify_client(id_client)
        self.em_queue.send(ack_msg(body))
        with self.lock:
            self.queries_ended[id_client, id_query] = True

    def __verify_client(self, id_client):
        if id_client not in self.ids_clients:
            self.__add_client(id_client)

    def __delete_client(self, id_client):
        self.__delete_from_dict(self.queries_ended, id_client)
        self.__delete_from_dict(self.queries_results, id_client)
        self.ids_clients.discard(id_client)
        print(f"action: delete_client | result: success | id_client: {id_client}")

    def __delete_from_dict(self, dict_clients, id_client):
        with self.lock:
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

            self.clients_handlers.stop()
            self.running = False

        sys.exit(0)
