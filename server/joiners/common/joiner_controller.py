import signal, sys
from server.common.queue.connection import Connection
from server.common.utils_messages_client import *
from server.common.utils_messages_eof import ack_msg


class JoinerController:
    def __init__(
        self,
        name_recv_queue,
        name_trips_queue,
        name_em_queue,
        name_next_stage_queue,
        joiner,
    ):
        self.__init_joiner(joiner)

        self.__connect(
            name_recv_queue, name_trips_queue, name_em_queue, name_next_stage_queue
        )

        self.__run()

    def __init_joiner(self, joiner):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.joiner = joiner
        print("action: joiner_started | result: success")

    def __connect(
        self, name_recv_queue, name_trips_queue, name_em_queue, name_next_stage_queue
    ):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.basic_queue(name_recv_queue)
            self.trips_queue = self.queue_connection.basic_queue(name_trips_queue)
            self.em_queue = self.queue_connection.pubsub_queue(name_em_queue)
            self.next_stage_queue = self.queue_connection.pubsub_queue(
                name_next_stage_queue
            )
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def __run(self):
        """
        start receiving messages.
        """
        self.recv_queue.receive(self.process_messages)
        self.queue_connection.start_receiving()

    def process_messages(self, ch, method, properties, body):
        if is_eof(body):
            self.__last_static_data_arrived()
        else:
            self.__static_data_arrived(body)

    def __last_static_data_arrived(self):
        print(
            "action: static_data_arrived | result: success | msg: starting to receive trips"
        )
        self.amount_joined = 0
        self.trips_queue.receive(self.process_join_messages)

    def __static_data_arrived(self, body):
        header, chunk_data = decode(body)
        city = obtain_city(header)

        self.__add_chunk_data(chunk_data, city)

    def __add_chunk_data(self, chunk_data, city):
        """
        stores all of the chunk of data.
        """
        for data in chunk_data:
            data = data.split(",")
            self.joiner.add_data(city, data)

    def process_join_messages(self, ch, method, properties, body):
        if is_eof(body):
            self.__last_trip_arrived()
        else:
            self.__request_join_arrived(body)

    def __request_join_arrived(self, body):
        header, trips = decode(body)
        city = obtain_city(header)

        joined_trips = self.__join_trips(trips, city)
        self.__send_next_stage(header, joined_trips)

    def __join_trips(self, trips, city):
        """
        try to join each trip in the chunk.
        returns the result of each successful join operation.
        """
        joined_trips = []

        for trip in trips:
            trip = trip.split(",")
            ret = self.joiner.join_trip(city, trip)
            if ret:
                self.amount_joined += 1
                joined_trips.append(ret)

        return joined_trips

    def __send_next_stage(self, header, joined_trips):
        if len(joined_trips) > 0:
            msg = construct_msg(header, joined_trips)
            self.next_stage_queue.send(msg)

    def __last_trip_arrived(self):
        self.em_queue.send(ack_msg())
        print(f"action: eof_trips_arrived | amount_joined: {self.amount_joined}")

    def stop(self, *args):
        if self.running:
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )

            self.running = False

        sys.exit(0)
