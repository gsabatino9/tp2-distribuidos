import signal
from threading import Thread
from server.common.queue.connection import Connection
from server.common.utils_messages_new_client import decode_reply


class ReceiverIds(Thread):
    def __init__(self, name_recv_ids_queue, clients_connections, clients_queues):
        super().__init__()
        self.__init_receiver_ids(clients_connections, clients_queues)
        self.__connect_queue(name_recv_ids_queue)

    def __init_receiver_ids(self, clients_connections, clients_queues):
        self.running = True
        self.clients_connections = clients_connections
        self.clients_queues = clients_queues

        print("action: receiver_ids_started | result: success")

    def __connect_queue(self, name_recv_ids_queue):
        try:
            self.queue_connection = Connection()
            self.recv_ids_queue = self.queue_connection.basic_queue(
                name_recv_ids_queue
            )
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def run(self):
        self.recv_ids_queue.receive(self.receive_id)
        try:
            self.queue_connection.start_receiving()
        except:
            if self.running:
                print("error.")

    def receive_id(self, body):
        id_client, is_session_accepted = decode_reply(body)
        for queue_client in self.clients_queues:
            queue_client.put((id_client, is_session_accepted))

        print(f"action: id_arrived_client | result: success | id_client: {id_client}")

    def stop(self):
        if self.running:
            self.running = False
            try:
                self.queue_connection.stop_receiving()
            except:
                # if doest not have queue_connection yet
                pass
