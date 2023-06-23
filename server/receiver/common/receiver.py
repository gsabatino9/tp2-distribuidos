import socket, signal, sys, queue
from protocol.communication_server import CommunicationServer
from server.common.queue.connection import Connection
from common.utils import is_eof
from common.receiver_ids import ReceiverIds
from common.client_handler import ClientHandler
from server.common.utils_messages_eof import eof_msg
from server.common.utils_messages_client import is_station, is_weather, encode_header


class Receiver:
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
        max_clients=5,
    ):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.amount_queries = amount_queries
        self.accepter_socket = self.__create_socket(host, port)
        self.clients_connections = {}
        self.max_clients = max_clients
        self.recv_ids = ReceiverIds(name_recv_ids_queue, self.clients_connections)

        self.name_stations_queue = name_stations_queue
        self.name_weather_queue = name_weather_queue
        self.name_trips_queues = name_trips_queues
        self.name_session_manager_queue = name_session_manager_queue
        self.name_em_queue = name_em_queue

        print("action: receiver_started | result: success")

    def __create_socket(self, host, port):
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.bind((host, port))

        return skt

    def run(self):
        self.recv_ids.start()
        self.accepter_socket.listen(self.max_clients)
        print(f"action: waiting_clients | result: success")

        self.clients_handlers = []
        while self.running:
            client_handler = self.__accept_client()
            client_handler.start()
            self.clients_handlers.append(client_handler)

        for client_handler in self.clients_handlers:
            client_handler.join()

        self.recv_ids.join()

    def __accept_client(self):
        client_socket, _ = self.accepter_socket.accept()
        client_connection = CommunicationServer(client_socket)
        client_address = client_connection.getpeername()[0]
        print(
            f"action: client_connected | result: success | msg: starting to receive data | client_address: {client_address}"
        )

        queue_client = queue.Queue()
        self.clients_connections[client_address] = (
            queue_client,
            client_connection,
        )
        return ClientHandler(
            client_address,
            queue_client,
            client_connection,
            self.name_stations_queue,
            self.name_weather_queue,
            self.name_trips_queues,
            self.name_session_manager_queue,
            self.name_em_queue,
            self.amount_queries
        )

    def stop(self, *args):
        if self.running:
            self.queue_connection.close()
            self.recv_ids.stop()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )
            if hasattr(self, "clients_connections"):
                for _, client_connection in self.clients_connections.values():
                    # TODO: try-catch
                    try:
                        client_connection.stop()
                        print(
                            "action: close_resource | result: success | resource: client_connection"
                        )
                    except:
                        # ya fue cerrada antes la conexión
                        pass

            self.running = False

        sys.exit(0)
