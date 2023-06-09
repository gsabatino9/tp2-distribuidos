import signal, sys
from server.common.queue.connection import Connection
from server.common.utils_messages_eof import *
from server.common.utils_messages_status import get_id_client_from_msg


class EOFManager:
    def __init__(
        self,
        name_recv_queue,
        name_send_queue,
        name_stations_queue,
        name_weather_queue,
        name_join_stations_queue,
        name_join_weather_queue,
        name_status_queue,
    ):
        self.__init_eof_manager()
        self.__connect(
            name_recv_queue,
            name_send_queue,
            name_stations_queue,
            name_weather_queue,
            name_join_stations_queue,
            name_join_weather_queue,
            name_status_queue,
        )
        self.__run()

    def __init_eof_manager(self):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.acks = 0

        print("action: eof_manager_started | result: success")

    def __connect(
        self,
        name_recv_queue,
        name_send_queue,
        name_stations_queue,
        name_weather_queue,
        name_join_stations_queue,
        name_join_weather_queue,
        name_status_queue,
    ):
        try:
            self.queue_connection = Connection()
            self.send_queue = self.queue_connection.pubsub_queue(name_send_queue)
            self.recv_queue = self.queue_connection.pubsub_queue(name_recv_queue)
            self.stations_queue = self.queue_connection.basic_queue(name_stations_queue)
            self.weather_queue = self.queue_connection.basic_queue(name_weather_queue)

            self.join_stations_queue = self.queue_connection.basic_queue(
                name_join_stations_queue
            )
            self.join_weather_queue = self.queue_connection.basic_queue(
                name_join_weather_queue
            )

            self.status_queue = self.queue_connection.pubsub_queue(name_status_queue)

        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def __run(self):
        """
        start receiving messages.
        """
        self.status_queue.receive(self.receive_new_client)
        self.recv_queue.receive(self.receive_msg)
        self.queue_connection.start_receiving()

    def receive_new_client(self, ch, method, properties, body):
        id_new_client = get_id_client_from_msg(body)
        print(f"action: new_client | result: success | id_new_client: {id_new_client}")

    def receive_msg(self, ch, method, properties, body):
        header = decode(body)

        if is_eof(header):
            self.__send_eof(header, body)
        else:
            self.__recv_ack_trips(header, body)

    def __send_eof(self, header, msg):
        """
        it sends EOF to each known worker, depends on the type of EOF.
        """
        print(f"action: send_eofs | result: success | msg: eof arrived")
        if is_station(header):
            self.stations_queue.send(msg)
        elif is_weather(header):
            self.weather_queue.send(msg)
        else:
            self.join_stations_queue.send(msg)
            self.join_weather_queue.send(msg)

    def __recv_ack_trips(self, header, body):
        """
        if the number of workers (for that type of data) that returned ack reaches the maximum count, it sends EOF to the next stage.
        """
        self.acks += 1

        if self.acks == 2:
            print(
                f"action: close_stage | result: success | msg: all the sent EOFs have received ACK"
            )
            self.send_queue.send(eof_msg(header))

    def stop(self, *args):
        if self.running:
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )

            self.running = False

        sys.exit(0)
