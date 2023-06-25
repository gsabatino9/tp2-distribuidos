import signal, sys
from server.common.queue.connection import Connection
from server.common.utils_messages_client import *
from server.common.utils_messages_eof import ack_msg, get_id_client
from server.common.keep_alive.keep_alive import KeepAlive


class JoinerController:
    def __init__(
        self,
        name_recv_queue,
        name_trips_queue,
        name_em_queue,
        name_next_stage_queue,
        joiner,
        is_static_data,
    ):
        self.__init_joiner(joiner, is_static_data)

        self.__connect(
            name_recv_queue, name_trips_queue, name_em_queue, name_next_stage_queue
        )

        self.__run()

    def __init_joiner(self, joiner, is_static_data):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.joiner = joiner
        self.is_static_data = is_static_data
        self.keep_alive = KeepAlive()
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
        self.keep_alive.start()
        self.recv_queue.receive(self.process_messages)
        try:
            self.queue_connection.start_receiving()
        except:
            if self.running:
                raise  # gracefull quit
        self.keep_alive.stop()
        self.keep_alive.join()

    def process_messages(self, body):
        try:
            header, payload = decode(body)
            is_eof = False
        except:
            is_eof = True

        if is_eof:
            self.__last_trip_arrived(body)
        elif self.is_static_data(header):
            self.__static_data_arrived(header, payload)
        else:  # is_trip
            self.__request_join_arrived(header, payload)

    def __static_data_arrived(self, header, chunk_data):
        self.__add_chunk_data(header.id_client, chunk_data)

    def __add_chunk_data(self, id_client, chunk_data):
        """
        stores all of the chunk of data.
        """
        for data in chunk_data:
            data = data.split(",")
            self.joiner.add_data(id_client, data)

    def __request_join_arrived(self, header, trips):
        joined_trips = self.__join_trips(header.id_client, trips)
        self.__send_next_stage(header, joined_trips)

    def __join_trips(self, id_client, trips):
        """
        try to join each trip in the chunk.
        returns the result of each successful join operation.
        """
        joined_trips = []

        for trip in trips:
            trip = trip.split(",")
            ret = self.joiner.join_trip(id_client, trip)
            if ret:
                joined_trips.append(ret)

        return joined_trips

    def __send_next_stage(self, header, joined_trips):
        if len(joined_trips) > 0:
            msg = construct_msg(header, joined_trips)
            self.next_stage_queue.send(msg)

    def __last_trip_arrived(self, body):
        self.joiner.delete_client(get_id_client(body))
        self.em_queue.send(ack_msg(body))

    def stop(self, *args):
        if self.running:
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )

            self.running = False
