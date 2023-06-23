from threading import Thread
from server.common.queue.connection import Connection
from server.common.utils_messages_eof import eof_msg
from server.common.utils_messages_client import is_station, is_weather, encode_header
from common.utils import is_eof


class ClientHandler(Thread):
    def __init__(
        self,
        client_address,
        queue_client,
        client_connection,
        name_stations_queue,
        name_weather_queue,
        name_trips_queues,
        name_session_manager_queue,
        name_em_queue,
        amount_queries
    ):
        super().__init__()
        self.client_address = client_address
        self.queue_client = queue_client
        self.client_connection = client_connection
        self.name_stations_queue = name_stations_queue
        self.name_weather_queue = name_weather_queue
        self.name_trips_queues = name_trips_queues
        self.name_session_manager_queue = name_session_manager_queue
        self.name_em_queue = name_em_queue
        self.amount_queries = amount_queries

    def run(self):
        self.__connect_queues()

        # TODO: no enviarlo en caso de que el request del cliente
        # sea de otro tipo
        self.session_manager_queue.send(self.client_address)
        not_assigned = self.__assign_id_to_client()
        if not_assigned:
            print(f"action: close_client | msg: max clients in system")
            # TODO: hacer que no se cierre el cliente, sino que se espere
            # al request del mismo.
            self.__close_client()
        else:
            self.__run_loop_client()

    def __assign_id_to_client(self):
        id_client = self.queue_client.get()
        if id_client == 0:
            return True
        else:
            self.client_connection.send_id_client(id_client)
            return False

    def __run_loop_client(self):
        types_ended = set()

        while len(types_ended) < self.amount_queries:
            header, payload_bytes = self.client_connection.recv_data(decode_payload=False)

            if is_eof(header):
                types_ended.add(header.data_type)
                self.__send_eof(header)
            else:
                self.__route_message(header, payload_bytes)

            self.__send_ack_client(header.id_batch)

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

    def __send_ack_client(self, id_batch):
        """
        informs the client that bach with id_batch arrived successfully.
        """
        self.client_connection.send_ack_batch(id_batch)    

    def __connect_queues(self):
        try:
            self.queue_connection = Connection()
            self.stations_queue = self.queue_connection.basic_queue(self.name_stations_queue)
            self.weather_queue = self.queue_connection.basic_queue(self.name_weather_queue)
            self.trips_queues = [
                self.queue_connection.basic_queue(q) for q in self.name_trips_queues
            ]
            self.session_manager_queue = self.queue_connection.pubsub_queue(
                self.name_session_manager_queue
            )
            self.em_queue = self.queue_connection.pubsub_queue(self.name_em_queue)
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()        

    def __close_client(self):
        self.client_connection.stop()