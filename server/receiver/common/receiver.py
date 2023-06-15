import socket, signal, sys
from multiprocessing import Pool, Process
from protocol.communication_server import CommunicationServer
from server.common.queue.connection import Connection
from common.utils import is_eof
from server.common.utils_messages_eof import eof_msg
from server.common.utils_messages_client import is_station, is_weather, encode_header
from server.common.utils_messages_status import id_client_msg
from random import randint


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
        amount_queries,
        max_clients=5,
    ):
        self.__init_receiver(amount_queries, host, port, max_clients)

        self.__connect_queue(name_stations_queue, name_weather_queue, name_trips_queues)
        self.__connect_eof_manager_queue(name_em_queue)
        self.__connect_status_queue(name_status_queue)

    def __init_receiver(self, amount_queries, host, port, max_clients):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.amount_queries = amount_queries
        self.accepter_socket = self.__create_socket(host, port)
        self.clients_connections = {}
        self.max_clients = max_clients

        print("action: receiver_started | result: success")

    def __connect_queue(
        self, name_stations_queue, name_weather_queue, name_trips_queues
    ):
        try:
            self.queue_connection = Connection()
            self.stations_queue = self.queue_connection.basic_queue(name_stations_queue)
            self.weather_queue = self.queue_connection.basic_queue(name_weather_queue)
            self.trips_queues = [
                self.queue_connection.basic_queue(q) for q in name_trips_queues
            ]
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def __connect_eof_manager_queue(self, name_em_queue):
        self.em_queue = self.queue_connection.pubsub_queue(name_em_queue)

    def __connect_status_queue(self, name_status_queue):
        self.status_queue = self.queue_connection.pubsub_queue(name_status_queue)

    def __create_socket(self, host, port):
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.bind((host, port))

        return skt

    def run(self):
        self.accepter_socket.listen(self.max_clients)
        print(f"action: waiting_clients | result: success")
        #with Pool(processes=5) as pool:
        while self.running:
            client_connection = self.__accept_client()
            # pool.apply_async(self.__handle_client, (client_connection,))
            process = Process(
                target=self.__handle_client, args=(client_connection,)
            )
            process.start()

    def __accept_client(self):
        client_socket, client_address = self.accepter_socket.accept()
        client_connection = CommunicationServer(client_socket)
        self.clients_connections[client_address] = client_connection
        id_client = self.__asign_id_to_client(client_connection)

        print(
            f"action: client_connected | result: success | msg: starting to receive data | id_client: {id_client}"
        )

        return client_connection

    def __handle_client(self, client_connection):
        types_ended = set()

        while len(types_ended) < self.amount_queries:
            header, payload_bytes = client_connection.recv_data(decode_payload=False)

            if is_eof(header):
                types_ended.add(header.data_type)
                self.__send_eof(header)
            else:
                self.__route_message(header, payload_bytes)

            # después de poner el msg en la cola, le mando ack
            self.__send_ack_client(header.id_batch, client_connection)

    def __asign_id_to_client(self, client_connection):
        id_client = self.__get_id_client()
        client_connection.send_id_client(id_client)
        self.__inform_new_client(id_client)

        return id_client

    def __get_id_client(self):
        return randint(0, 250)

    def __inform_new_client(self, id_client):
        self.status_queue.send(id_client_msg(id_client))

    def __send_eof(self, header):
        self.em_queue.send(eof_msg(header))

    def __route_message(self, header, payload_bytes):
        """
        send the message according to the type of header.
        """
        msg = encode_header(header) + payload_bytes

        if is_station(header):
            self.stations_queue.send(msg)
        elif is_weather(header):
            self.weather_queue.send(msg)
        else:
            self.__send_msg_to_trips(msg)

    def __send_msg_to_trips(self, msg):
        [trips_queue.send(msg) for trips_queue in self.trips_queues]

    def __send_ack_client(self, id_batch, client_connection):
        """
        informs the client that bach with id_batch arrived successfully.
        """
        client_connection.send_ack_batch(id_batch)

    def stop(self, *args):
        if self.running:
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )
            if hasattr(self, "clients_connections"):
                for client_connection in self.clients_connections.values():
                    client_connection.stop()
                    print(
                        "action: close_resource | result: success | resource: client_connection"
                    )

            self.running = False

        sys.exit(0)
