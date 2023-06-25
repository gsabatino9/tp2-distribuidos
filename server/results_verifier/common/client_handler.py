import queue
from threading import Thread
from server.common.utils_messages_client import is_eof, is_last_message
from server.common.queue.connection import Connection


class ClientHandler(Thread):
    def __init__(
        self,
        client_connection,
        name_session_manager_queue,
        name_send_exchange,
        name_send_queue,
    ):
        super().__init__()
        self.client_connection = client_connection
        self.client_address = self.client_connection.getpeername()[0]
        self.name_session_manager_queue = name_session_manager_queue
        self.name_send_exchange = name_send_exchange
        self.name_send_queue = name_send_queue

    def run(self):
        self.__connect_queues()

        header, _ = self.client_connection.recv_data(decode_payload=False)
        self.__connect_client(header.id_client)

        self.recv_queue.receive(self.process_batch)
        self.queue_connection.start_receiving()

        self.queue_connection.close()

    def process_batch(self, body):
        if is_eof(body):
            self.client_connection.send_results(body, is_last=True)
            self.__stop_connection()
        else:
            self.client_connection.send_results(body, is_last=False)

    def __connect_queues(self):
        try:
            self.queue_connection = Connection()
            self.session_manager_queue = self.queue_connection.pubsub_queue(
                self.name_session_manager_queue
            )
            self.recv_queue = self.queue_connection.routing_building_queue(
                self.name_send_exchange, self.name_send_queue
            )
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")

    def __connect_client(self, id_client):
        self.recv_queue.bind_queue(str(id_client))

    def __stop_connection(self):
        self.session_manager_queue.send(self.client_address)
        self.queue_connection.stop_receiving()
        self.client_connection.stop()
