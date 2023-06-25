import signal, sys
from server.common.queue.connection import Connection
from server.common.utils_messages_eof import *
from server.common.utils_messages_status import get_id_client_from_msg
from server.common.keep_alive.keep_alive import KeepAlive


class EOFManager:
    def __init__(
        self, name_recv_queue, name_verifier_queue, name_status_queue, size_queries
    ):
        self.__init_eof_manager(size_queries)
        self.__connect(name_recv_queue, name_verifier_queue, name_status_queue)
        self.__run()

    def __init_eof_manager(self, size_queries):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.clients_acks = {}
        self.size_queries = size_queries
        self.keep_alive = KeepAlive()
        print("action: eof_manager_started | result: success")

    def __connect(self, name_recv_queue, name_verifier_queue, name_status_queue):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.pubsub_queue(name_recv_queue)
            self.verifier_queue = self.queue_connection.routing_queue(
                name_verifier_queue
            )
            self.status_queue = self.queue_connection.pubsub_queue(name_status_queue)
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def __run(self):
        """
        start receiving messages.
        """
        self.keep_alive.start()
        self.status_queue.receive(self.receive_new_client)
        self.recv_queue.receive(self.receive_msg)
        try:
            self.queue_connection.start_receiving()
        except Exception as e:
            if self.running:
                print(f"action: middleware_error | error: {str(e)}")
        except:
            if self.running:
                print(f"action: middleware_error | error: unknown.")
        self.keep_alive.stop()
        self.keep_alive.join()

    def receive_new_client(self, ch, method, properties, body):
        id_new_client = get_id_client_from_msg(body)
        print(f"action: new_client | result: success | id_new_client: {id_new_client}")

    def receive_msg(self, ch, method, properties, body):
        header = decode(body)
        self.__verify_client(header.id_client)

        if is_eof(header):
            self.__send_eofs(header, body)
        else:
            self.__recv_ack_trips(header, body)

    def __verify_client(self, id_client):
        if id_client not in self.clients_acks:
            self.clients_acks[id_client] = 0

    def __send_eofs(self, header, msg):
        """
        it sends EOF to the results verifier controller for each query.
        """
        print(f"action: send_eofs | result: success | msg: eof arrived")
        for i in range(1, self.size_queries + 1):
            self.verifier_queue.send(msg, routing_key=str(i))

    def __recv_ack_trips(self, header, body):
        """
        if the number of queries that returned ack reaches the maximum count, it ends.
        """
        self.clients_acks[header.id_client] += 1

        if self.clients_acks[header.id_client] == self.size_queries:
            print(
                f"action: close_stage | result: success | id_client: {header.id_client}"
            )
            del self.clients_acks[header.id_client]

    def stop(self, *args):
        if self.running:
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )

            self.running = False

        
