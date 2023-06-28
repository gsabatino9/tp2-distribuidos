import socket, signal, sys, queue
from threading import Thread
from protocol.communication_server import CommunicationServer
from common.client_handler import ClientHandler


class ResultsSender(Thread):
    def __init__(
        self,
        name_session_manager_queue,
        name_request_queue,
        address,
        client_handlers_queues,
    ):
        super().__init__()
        self.running = True

        self.accepter_socket = self.__create_socket(address)
        self.clients_handlers = []
        self.clients_handlers_queue = queue.Queue()

        for i, queue_results in enumerate(client_handlers_queues):
            client_handler = ClientHandler(
                name_session_manager_queue,
                name_request_queue,
                self.clients_handlers_queue,
                queue_results,
                i,
            )
            client_handler.start()
            self.clients_handlers.append(client_handler)

        print("action: results_sender_started | result: success")

    def __create_socket(self, address):
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.bind(address)

        return skt

    def run(self):
        self.__run_accept_loop()
        self.__join_clients()

    def __run_accept_loop(self):
        self.accepter_socket.listen()
        print(f"action: waiting_clients | result: success")
        self.clients = []

        while self.running:
            self.__accept_client()

    def __join_clients(self):
        [client_handler.stop() for client_handler in self.clients_handlers]
        [client_handler.join() for client_handler in self.clients_handlers]

        self.accepter_socket.close()

    def __accept_client(self):
        try:
            client_socket, client_address = self.accepter_socket.accept()
        except:
            if self.running:
                raise
            return
        client_connection = CommunicationServer(client_socket)

        print(
            f"action: client_connected | result: success | msg: starting to receive data"
        )

        self.clients_handlers_queue.put(client_connection)

    def stop(self):
        if self.running:
            self.running = False
            self.accepter_socket.shutdown(socket.SHUT_RDWR)
            print(
                "action: close_resource | result: success | resource: accepter_socket"
            )
