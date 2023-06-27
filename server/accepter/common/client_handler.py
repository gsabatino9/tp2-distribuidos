import struct, socket
from threading import Thread
from server.common.queue.connection import Connection
from server.common.utils_messages_eof import eof_msg
from server.common.utils_messages_client import is_station, is_weather, encode_header
from common.utils import is_get_id, is_eof


class ClientHandler(Thread):
    def __init__(
        self,
        accepter_queue,
        queue_client,
        name_stations_queue,
        name_weather_queue,
        nodes_to_send_trips_direct,
        name_session_manager_queue,
        name_em_queue,
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
        self.name_em_queue = name_em_queue
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
        self.client_address = self.client_connection.getpeername()[0]
        self.active = True
        while self.active and self.running:
            try:
                header, payload_bytes = self.client_connection.recv_data(
                    decode_payload=False
                )

                if is_get_id(header):
                    self.__assign_id_to_client()
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

        self.client_connection.stop()

    def __assign_id_to_client(self):
        self.session_manager_queue.send(self.client_address)

        id_client = -1
        while True:
            id_client, client_address = self.queue_client.get()
            if not self.running:
                return

            if client_address == self.client_address:
                break

        if id_client == 0:
            self.client_connection.send_error_message()
        else:
            self.client_connection.send_id_client(id_client)

    def __send_eof(self, header):
        self.em_queue.send(eof_msg(header))

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
                self.queue_connection.sharding_queue(
                    queue_name, size_node, 1
                )
                for queue_name, size_node in self.nodes_to_send_trips_direct
            ]
            self.session_manager_queue = self.queue_connection.pubsub_queue(
                self.name_session_manager_queue
            )
            self.em_queue = self.queue_connection.pubsub_queue(self.name_em_queue)
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
