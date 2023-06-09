import socket, signal, sys
from protocol.communication_server import CommunicationServer
from server.common.queue.connection import Connection
from server.common.utils_messages_eof import ack_msg, get_id_client
from server.common.utils_messages_group import decode, is_eof


class ResultsVerifier:
    def __init__(self, name_recv_queue, name_em_queue, host, port, amount_queries):
        self.__init_results_verifier(host, port, amount_queries)
        self.__connect(name_recv_queue, name_em_queue, amount_queries)
        self.__run()

    def __init_results_verifier(self, host, port, amount_queries):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.ids_clients = set()
        self.queries_results = {}
        self.queries_ended = {}
        self.amount_queries = amount_queries
        self.addr = (host, port)

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

    def __run(self):
        """
        start receiving messages.
        """
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

        self.queries_results[id_client, id_query] += results

    def __add_client(self, id_client):
        print(f"action: add_client | result: success | id_client: {id_client}")
        self.ids_clients.add(id_client)
        for id_query in range(1, self.amount_queries+1):
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

        if ended:
            print(
                f"action: results_ready | id_client: {id_client} | results: {self.queries_results}"
            )
            self.__inform_results(id_client)
            self.__delete_client(id_client)

    def __inform_results(self, id_client):
        self.__connect_with_client()
        self.__send_results(id_client)

    def __delete_client(self, id_client):
        self.__delete_from_dict(self.queries_ended, id_client)
        self.__delete_from_dict(self.queries_results, id_client)
        self.ids_clients.discard(id_client)
        print(f"action: delete_client | result: success | id_client: {id_client}")

    def __delete_from_dict(self, dict_clients, id_client):
        keys_to_delete = [key for key in dict_clients.keys() if key[0] == id_client]
        for key in keys_to_delete:
            del dict_clients[key]

    def __connect_with_client(self):
        """
        it connects to the client in order to inform it of the results.
        """
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.bind(self.addr)
        skt.listen()

        client_socket, _ = skt.accept()
        self.client_connection = CommunicationServer(client_socket)
        print(
            "action: client_connected | result: success | msg: starting to send results"
        )

    def __send_results(self, id_client):
        """
        it sends each list of results for each query.
        Note: the protocol defines a maximum chunk size for sending.
        """
        for query in self.queries_results:
            if query[0] == id_client:
                results = self.queries_results[query]
                if len(results) > 0:
                    self.client_connection.send_results(query[1], results)

        self.client_connection.send_last()
        print("action: results_sent | result: success")

    def stop(self, *args):
        if self.running:
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )
            if hasattr(self, "client_connection"):
                self.client_connection.stop()
                print(
                    "action: close_resource | result: success | resource: client_connection"
                )

            self.running = False

        sys.exit(0)
