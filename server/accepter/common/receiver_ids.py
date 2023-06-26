import signal
from threading import Thread
from server.common.queue.connection import Connection
from server.common.utils_messages_new_client import decode


class ReceiverIds(Thread):
    def __init__(self, name_recv_ids_queue, clients_connections, clients_queues):
        super().__init__()
        self.__init_receiver_ids(clients_connections, clients_queues)
        self.__connect_queue(name_recv_ids_queue)

    def __init_receiver_ids(self, clients_connections, clients_queues):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.clients_connections = clients_connections
        self.clients_queues = clients_queues

        print("action: receiver_ids_started | result: success")

    def __connect_queue(self, name_recv_ids_queue):
        try:
            self.queue_connection = Connection()
            self.recv_ids_queue = self.queue_connection.pubsub_queue(
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
                raise  # gracefull quit

    def receive_id(self, body):
        id_client, client_address = decode(body)
        for queue_client in self.clients_queues:
            queue_client.put((id_client, client_address))
        
        print(
            f"action: id_arrived_client | result: success | id_client: {id_client}"
        )

    def stop(self, *args):
        if self.running:
            self.queue_connection.close()
            self.running = False
