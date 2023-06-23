import socket, signal, sys
from threading import Thread
from protocol.communication_server import CommunicationServer
from common.client_handler import ClientHandler


class ResultsSender(Thread):
    def __init__(
        self,
        address,
        name_session_manager_queue,
        name_send_exchange,
        name_send_queue,
        max_clients=5,
    ):
        super().__init__()
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.accepter_socket = self.__create_socket(address)
        self.max_clients = max_clients
        self.clients_handlers = []
        self.name_session_manager_queue = name_session_manager_queue
        self.name_send_exchange = name_send_exchange
        self.name_send_queue = name_send_queue

        print("action: results_sender_started | result: success")

    def __create_socket(self, address):
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.bind(address)

        return skt

    def run(self):
        self.__run_accept_loop()
        self.__join_clients()

    def __run_accept_loop(self):
        self.accepter_socket.listen(self.max_clients)
        print(f"action: waiting_clients | result: success")
        self.clients = []

        while self.running:
            client_handler = self.__accept_client()
            client_handler.start()
            self.clients_handlers.append(client_handler)

    def __join_clients(self):
        for client_handler in self.clients_handlers:
            client_handler.join()

        self.accepter_socket.close()

    def __accept_client(self):
        client_socket, client_address = self.accepter_socket.accept()
        client_connection = CommunicationServer(client_socket)

        print(
            f"action: client_connected | result: success | msg: starting to receive data"
        )

        return ClientHandler(
            client_connection,
            self.name_session_manager_queue,
            self.name_send_exchange,
            self.name_send_queue,
        )

    def stop(self, *args):
        if self.running:
            self.accepter_socket.close()
            print(
                "action: close_resource | result: success | resource: accepter_socket"
            )
            self.running = False

        sys.exit(0)
