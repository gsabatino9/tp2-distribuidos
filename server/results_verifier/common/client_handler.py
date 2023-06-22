import queue
from threading import Thread
from server.common.utils_messages_client import is_eof
from server.common.queue.connection import Connection


class ClientHandler(Thread):
    def __init__(
        self,
        clients_queues,
        lock_clients_queues,
        client_connection,
        name_session_manager_queue,
    ):
        super().__init__()
        self.__init_client_handler(
            clients_queues, lock_clients_queues, client_connection
        )
        self.__connect_queue(name_session_manager_queue)

    def __init_client_handler(
        self, clients_queues, lock_clients_queues, client_connection
    ):
        self.clients_queues = clients_queues
        self.lock_clients_queues = lock_clients_queues

        self.client_connection = client_connection
        self.client_address = self.client_connection.getpeername()[0]

    def __connect_queue(self, name_session_manager_queue):
        try:
            self.queue_connection = Connection()
            self.session_manager_queue = self.queue_connection.pubsub_queue(
                name_session_manager_queue
            )
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def run(self):
        # recv request for info
        header, _ = self.client_connection.recv_data(decode_payload=False)
        self.__connect_client(header.id_client)

        # start receving batches
        ended = False
        while not ended:
            msg = self.clients_queues[header.id_client].get()
            ended = self.__process_batch(msg)

        self.__end_session_client()

    def __connect_client(self, id_client):
        with self.lock_clients_queues:
            if id_client not in self.clients_queues:
                self.clients_queues[id_client] = queue.Queue()

    def __process_batch(self, msg):
        if is_eof(msg):
            self.client_connection.send_results(msg, is_last=True)
            self.__stop_connection()
            return True
        else:
            self.client_connection.send_results(msg, is_last=False)
            return False

    def __end_session_client(self):
        self.session_manager_queue.send(self.client_address)
        self.queue_connection.close()

    def __stop_connection(self):
        self.client_connection.stop()
