import queue
from threading import Thread
from server.common.utils_messages_client import last_message
from server.common.utils_messages_new_client import delete_client
from server.common.utils_messages_results import (
    request_message,
    is_error,
    delete_message,
)
from server.common.queue.connection import Connection


class ClientHandler(Thread):
    def __init__(
        self,
        name_session_manager_queue,
        name_request_queue,
        queue_client_connections,
        queue_results,
        id_client_handler,
    ):
        super().__init__()
        self.queue_client_connections = queue_client_connections
        self.queue_results = queue_results
        self.id_client_handler = id_client_handler

        self.name_session_manager_queue = name_session_manager_queue
        self.name_request_queue = name_request_queue

    def run(self):
        while True:
            self.client_connection = self.queue_client_connections.get()
            self.client_address = self.client_connection.get_addr()

            header, _ = self.client_connection.recv_data(decode_payload=False)
            self.__connect_queues()
            self.__send_request_results_verifier(header.id_client)
            results_batches = self.queue_results.get()

            if not is_error(results_batches):
                for batch in results_batches:
                    self.client_connection.send_results(batch, is_last=False)
                self.client_connection.send_results(last_message(), is_last=True)

                self.__stop_connection(header.id_client)

            self.client_connection.stop()
            self.queue_connection.close()

    def __connect_queues(self):
        try:
            self.queue_connection = Connection()
            self.session_manager_queue = self.queue_connection.pubsub_queue(
                self.name_session_manager_queue
            )
            self.request_queue = self.queue_connection.routing_queue(
                self.name_request_queue
            )
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")

    def __send_request_results_verifier(self, id_client):
        msg = request_message(self.id_client_handler, id_client)
        self.request_queue.send(msg, routing_key="request_results")

    def __stop_connection(self, id_client):
        self.request_queue.send(
            delete_message(id_client), routing_key="request_results"
        )

        self.session_manager_queue.send(delete_client(id_client))
        # self.client_connection.stop()
