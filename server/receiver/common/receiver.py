import socket, signal, sys
from protocol.communication_server import CommunicationServer
from server.common.queue.connection import Connection
from common.utils import is_eof
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
        amount_queries,
    ):
        self.__init_receiver(amount_queries)

        self.__connect_queue(name_stations_queue, name_weather_queue, name_trips_queues)
        self.__connect_eof_manager_queue(name_em_queue)
        self.__connect_client(host, port)

    def __init_receiver(self, amount_queries):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.amount_queries = amount_queries

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

    def __connect_client(self, host, port):
        try:
            skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            skt.bind((host, port))
            skt.listen()

            client_socket, _ = skt.accept()
            self.client_connection = CommunicationServer(client_socket)

            print(
                "action: client_connected | result: success | msg: starting to receive data"
            )
        except OSError as e:
            print(f"error: creating_client_connection | log: {e}")
            self.stop()

    def run(self):
        """
        runs a loop until the eof of all data types arrives.
        """
        types_ended = set()

        while len(types_ended) < self.amount_queries:
            header, payload_bytes = self.client_connection.recv_data(
                decode_payload=False
            )

            if is_eof(header):
                types_ended.add(header.data_type)
                self.__send_eof(header)
            else:
                self.__route_message(header, payload_bytes)

        self.__send_ack_client()

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

    def __send_ack_client(self):
        """
        informs the client that all files arrived successfully.
        """
        print("action: all_files_arrived | result: success")
        self.client_connection.send_files_received()

    def stop(self, *args):
        if self.running:
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )
            if hasattr(self, "client_connection"):
                self.client_connection.stop()
                print(
                    "action: close_resource | result: success | resource: client_connection"
                )

            self.running = False

        sys.exit(0)
