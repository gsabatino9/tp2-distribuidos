import struct, socket
from threading import Thread
from server.common.queue.connection import Connection
from server.common.utils_messages_eof import eof_msg
from server.common.utils_messages_client import is_station, is_weather, encode_header
from server.common.utils_messages_new_client import request_init_session, eof_sent
from common.utils import is_init_session, is_eof


class ClientHandler(Thread):
    def __init__(
        self,
        accepter_queue,
        queue_client,
        name_stations_queue,
        name_weather_queue,
        nodes_to_send_trips_direct,
        name_session_manager_queue,
        amount_queries,
        size_stations,
        size_weather,
        sharding_amount,
    ):
        super().__init__()
        self.running = True

        self.accepter_queue = accepter_queue
        self.queue_client = queue_client
        self.name_stations_queue = name_stations_queue
        self.name_weather_queue = name_weather_queue
        self.nodes_to_send_trips_direct = nodes_to_send_trips_direct
        self.name_session_manager_queue = name_session_manager_queue
        self.amount_queries = amount_queries
        self.size_stations = size_stations
        self.size_weather = size_weather
        self.sharding_amount = sharding_amount
        self.active = False

    def run(self):
        while self.running:
            self.client_connection = self.accepter_queue.get()
            if not self.client_connection or not self.running:
                break
            self.__connect_queues()
            self.__handle_client()
            self.queue_connection.close()
        print("termina el client handler")

    def __handle_client(self):
        self.active = True
        while self.active and self.running:
            try:
                header, payload_bytes = self.client_connection.recv_data(
                    decode_payload=False
                )

                if is_init_session(header):
                    self.__request_init_session(header.id_client)
                elif is_eof(header):
                    self.__send_eof(header)
                    self.__send_ack_client(header.id_batch)
                    self.active = False
                else:
                    self.__route_message(header, payload_bytes)
                    self.__send_ack_client(header.id_batch)
            except:
                print("action: client_clossed")
                self.active = False
                self.__send_eof(header)

        self.client_connection.stop()

    def __request_init_session(self, id_client):
        self.session_manager_queue.send(request_init_session(id_client))

        is_session_accepted = False
        while True:
            (id_client_recv, is_session_accepted) = self.queue_client.get()
            if not self.running:
                return

            if id_client_recv == id_client:
                break

        if is_session_accepted:
            self.client_connection.send_accepted_connection()
        else:
            self.client_connection.send_error_message()

    def __send_eof(self, header):
        self.session_manager_queue.send(eof_sent(header.id_client))

    def __route_message(self, header, payload_bytes):
        """
        send the message according to the type of header.
        """
        msg = encode_header(header) + payload_bytes

        if is_station(header):
            self.stations_queue.send_static(msg, header.id_client)
        elif is_weather(header):
            self.weather_queue.send_static(msg, header.id_client)
        else:
            self.__send_msg_to_trips(msg, header.id_client)

    def __send_msg_to_trips(self, msg, id_client):
        self.stations_queue.send_workers(msg, id_client)
        self.weather_queue.send_workers(msg, id_client)
        [trips_queue.send_workers(msg, id_client) for trips_queue in self.trips_queues]

    def __send_ack_client(self, id_batch):
        """
        informs the client that bach with id_batch arrived successfully.
        """
        self.client_connection.send_ack_batch(id_batch)

    def __connect_queues(self):
        try:
            self.queue_connection = Connection()
            self.stations_queue = self.queue_connection.sharding_queue(
                self.name_stations_queue, self.size_stations, self.sharding_amount
            )
            self.weather_queue = self.queue_connection.sharding_queue(
                self.name_weather_queue, self.size_weather, self.sharding_amount
            )
            self.trips_queues = [
                self.queue_connection.sharding_queue(queue_name, size_node, 1)
                for queue_name, size_node in self.nodes_to_send_trips_direct
            ]
            self.session_manager_queue = self.queue_connection.pubsub_queue(
                self.name_session_manager_queue
            )
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")

    def stop(self):
        if self.running:
            self.running = False
            if self.active:
                try:
                    self.client_connection.comm.socket.shutdown(socket.SHUT_RDWR)
                except:
                    print("error: shutdown_client_connection_failed")
            self.queue_client.put((None, None))
            self.accepter_queue.put(None)
