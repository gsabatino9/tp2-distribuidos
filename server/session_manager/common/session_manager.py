import signal, sys
from uuid import uuid4
from server.common.utils_messages_new_client import error_message, assigned_id_message
from server.common.queue.connection import Connection


class SessionManager:
    def __init__(
        self, max_clients, name_recv_queue, name_send_queue, name_end_session_queue
    ):
        self.__init_session_manager(max_clients)
        self.__connect_queue(name_recv_queue, name_send_queue, name_end_session_queue)

    def __init_session_manager(self, max_clients):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.max_clients = max_clients
        # (key: client_address), (value: id_client)
        self.active_clients = {}

        print("action: session_manager_started | result: success")

    def __connect_queue(self, name_recv_queue, name_send_queue, name_end_session_queue):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.pubsub_queue(name_recv_queue)
            self.send_queue = self.queue_connection.pubsub_queue(name_send_queue)
            self.end_session_queue = self.queue_connection.pubsub_queue(
                name_end_session_queue
            )
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def run(self):
        """
        start receiving messages.
        """
        self.recv_queue.receive(self.new_client_request)
        self.end_session_queue.receive(self.end_session)
        self.queue_connection.start_receiving()

    def new_client_request(self, ch, method, properties, body):
        """
        pueden pasar 3 cosas:
        - active_clients < max_clients: asigna id al cliente.
        - active_clients == max_clients: rechaza el id al cliente.
        - cliente ya se encuentra asignado: devuelve el id asignado.
        """
        client_address = body

        print(f"action: new_client_request | client_address: {client_address}")
        if client_address in self.active_clients:
            msg = assigned_id_message(
                self.active_clients[client_address], client_address
            )
        elif len(self.active_clients) < self.max_clients:
            id_client = self.__assign_id_to_client(client_address)
            msg = assigned_id_message(id_client, client_address)
        else:
            msg = error_message(client_address)
            print("action: id_assigned | result: failure")

        self.send_queue.send(msg)

    def __assign_id_to_client(self, address):
        id_client = uuid4().int >> 64
        self.active_clients[address] = id_client
        print(f"action: id_assigned | result: success | id: {id_client}")

        return id_client

    def end_session(self, ch, method, properties, body):
        client_address = body
        if client_address in self.active_clients:
            print(
                f"action: end_session | result: success | id_client: {self.active_clients[client_address]}"
            )
            del self.active_clients[client_address]

    def stop(self, *args):
        if self.running:
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )

            self.running = False

        sys.exit(0)
