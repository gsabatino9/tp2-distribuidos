import socket, signal, sys
from protocol.communication_server import CommunicationServer
from common.client_handler import ClientHandler


class ResultsSender:
    def __init__(self, host, port, name_recv_exchange, name_recv_queue, max_clients=5):
        self.__init_results_sender(host, port, name_recv_exchange, name_recv_queue, max_clients)

    def __init_results_sender(self, host, port, name_recv_exchange, name_recv_queue, max_clients):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.accepter_socket = self.__create_socket((host, port))
        self.max_clients = max_clients
        self.name_recv_exchange = name_recv_exchange
        self.name_recv_queue = name_recv_queue
        self.clients_handlers = []

        print("action: results_sender_started | result: success")

    def __create_socket(self, address):
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.bind(address)

        return skt

    def run(self):
        self.accepter_socket.listen(self.max_clients)
        print(f"action: waiting_clients | result: success")
        self.clients = []

        while self.running:
            client_connection = self.__accept_client()
            client_handler = ClientHandler(client_connection)
            client_handler.start()
            self.clients_handlers.append(client_handler)

        for client_handler in self.clients_handlers:
            client_handler.join()

        self.accepter_socket.close()

    def __accept_client(self):
        client_socket, client_address = self.accepter_socket.accept()
        client_connection = CommunicationServer(client_socket)

        print(
            f"action: client_connected | result: success | msg: starting to receive data"
        )

        return client_connection

    def stop(self, *args):
        if self.running:
            self.accepter_socket.close()
            print(
                "action: close_resource | result: success | resource: accepter_socket"
            )
            self.running = False

        sys.exit(0)
