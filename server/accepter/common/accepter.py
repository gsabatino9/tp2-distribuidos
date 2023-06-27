import socket, signal, sys, queue, random
from protocol.communication_server import CommunicationServer
from server.common.queue.connection import Connection
from common.utils import is_eof
from common.receiver_ids import ReceiverIds
from common.client_handler import ClientHandler
from server.common.utils_messages_eof import eof_msg
from server.common.utils_messages_client import is_station, is_weather, encode_header
from server.common.keep_alive.keep_alive import KeepAlive


class Accepter:
    def __init__(
        self,
        host,
        port,
        name_stations_queue,
        name_weather_queue,
        name_trips_queues,
        name_em_queue,
        name_status_queue,
        name_session_manager_queue,
        name_recv_ids_queue,
        amount_queries,
        size_stations,
        size_weather,
        sharding_amount,
        max_clients=5,
    ):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.amount_queries = amount_queries
        self.accepter_socket = self.__create_socket(host, port)
        self.clients_connections = {}
        self.max_clients = max_clients

        self.name_stations_queue = name_stations_queue
        self.name_weather_queue = name_weather_queue
        self.name_trips_queues = name_trips_queues
        self.name_session_manager_queue = name_session_manager_queue
        self.name_em_queue = name_em_queue
        queues = self.__create_client_handlers(size_stations, size_weather, sharding_amount)
        self.recv_ids = ReceiverIds(name_recv_ids_queue, self.clients_connections, queues)
        self.keep_alive = KeepAlive()
        print("action: accepter_started | result: success")

    def __create_socket(self, host, port):
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.bind((host, port))

        return skt

    def __create_client_handlers(self, size_stations, size_weather, sharding_amount):
        self.clients_handlers = []
        self.accepter_queue = queue.Queue(maxsize=3)
        queues = [queue.Queue() for _ in range(3)]

        # TODO: cambiar a parámetro.
        for i in range(3):
            client_handler = ClientHandler(
                self.accepter_queue,
                queues[i],
                self.name_stations_queue,
                self.name_weather_queue,
                self.name_trips_queues,
                self.name_session_manager_queue,
                self.name_em_queue,
                self.amount_queries,
                size_stations,
                size_weather,
                sharding_amount
            )
            client_handler.start()
            self.clients_handlers.append(client_handler)

        return queues

    def run(self):
        self.keep_alive.start()
        self.recv_ids.start()
        self.accepter_socket.listen(self.max_clients)
        print(f"action: waiting_clients | result: success")

        while self.running:
            self.__accept_client()

        for client_handler in self.clients_handlers:
            client_handler.join()

        self.recv_ids.join()
        self.keep_alive.stop()
        self.keep_alive.join()

    def __accept_client(self):
        client_socket, _ = self.accepter_socket.accept()
        client_connection = CommunicationServer(client_socket)
        self.accepter_queue.put(client_connection)
        print(
            f"action: client_connected | result: success | msg: starting to receive data | client_address: {client_connection.getpeername()}"
        )

    def stop(self, *args):
        if self.running:
            self.running = False

            self.accepter_socket.shutdown(socket.SHUT_RDWR)
            for client_handler in self.clients_handlers:
                try:
                    client_handler.stop()
                    self.accepter_queue.put_nowait(None)
                except queue.QueueFull:
                    pass

