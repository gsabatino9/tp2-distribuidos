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
        except Exception as e:
            if self.running:
                print(f"action: middleware_error | error: {str(e)}")
        except:
            if self.running:
                print(f"action: middleware_error | error: unknown.")
        self.keep_alive.stop()
        self.keep_alive.join()

    def process_messages(self, ):
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
        self.__add_chunk_data(header.id_client, chunk_data)

    def __add_chunk_data(self, id_client, chunk_data):
        """
        stores all of the chunk of data.
        """
        for data in chunk_data:
            data = data.split(",")
            self.joiner.add_data(id_client, data)

    def process_join_messages(self, body):
        if is_eof(body):
            self.__last_trip_arrived(body)
        else:
            self.__request_join_arrived(body)

    def __request_join_arrived(self, body):
        header, trips = decode(body)

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
                self.amount_joined += 1
                joined_trips.append(ret)

        return joined_trips

    def __send_next_stage(self, header, joined_trips):
        if len(joined_trips) > 0:
            msg = construct_msg(header, joined_trips)
            self.next_stage_queue.send(msg)

    def __last_trip_arrived(self, body):
        self.joiner.delete_client(get_id_client(body))
        self.em_queue.send(ack_msg(body))
        print(f"action: eof_trips_arrived | amount_joined: {self.amount_joined}")

    def stop(self, *args):
        if self.running:
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )

            self.running = False

        
