import signal, sys
from server.common.queue.connection import Connection
from server.common.utils_messages_client import *
from server.common.utils_messages_eof import ack_msg, get_id_client
from server.common.keep_alive.keep_alive import KeepAlive
from server.common.utils_messages import is_message_eof


class JoinerController:
    def __init__(
        self,
        name_recv_queue,
        name_trips_queue,
        name_em_queue,
        name_next_stage_queues,
        size_workers_next_stage,
        joiner,
        is_static_data,
    ):
        self.__init_joiner(
            joiner, is_static_data, size_workers_next_stage, name_recv_queue
        )

        self.__connect(
            name_recv_queue,
            name_trips_queue,
            name_em_queue,
            name_next_stage_queues,
            size_workers_next_stage,
        )

        self.__run()

    def __init_joiner(
        self, joiner, is_static_data, size_workers_next_stage, name_recv_queue
    ):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.joiner = joiner
        self.size_workers_next_stage = size_workers_next_stage
        self.is_static_data = is_static_data
        self.prefetch_limit = 1000
        self.current_fetch_count = 0
        self.keep_alive = KeepAlive()
        self.id_worker = name_recv_queue
        print("action: joiner_started | result: success")

    def __connect(
        self,
        name_recv_queue,
        name_trips_queue,
        name_em_queue,
        name_next_stage_queues,
        size_workers_next_stage,
    ):
        try:
            self.name_next_stage_queues = name_next_stage_queues

            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.basic_queue(
                name_recv_queue, auto_ack=False
            )
            self.trips_queue = self.queue_connection.basic_queue(name_trips_queue)
            self.em_queue = self.queue_connection.basic_queue(name_em_queue)
            self.next_stage_queues = self.queue_connection.multiple_queues(
                name_next_stage_queues, self.size_workers_next_stage
            )
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def __run(self):
        """
        start receiving messages.
        """
        self.keep_alive.start()
        self.recv_queue.receive(
            self.process_messages, prefetch_count=self.prefetch_limit
        )
        try:
            self.queue_connection.start_receiving()
        except:
            if self.running:
                raise  # gracefull quit
        self.keep_alive.stop()
        self.keep_alive.join()

    def process_messages(self, body):
        self.current_fetch_count += 1
        if self.current_fetch_count * 10 // 8 > self.prefetch_limit:
            self.__ack_messages()

        if is_message_eof(body):
            self.__last_trip_arrived(body)
            self.__ack_messages()
            return

        header, payload = decode(body)
        if self.is_static_data(header):
            self.__static_data_arrived(header, payload)
        else:  # is_trip
            self.__request_join_arrived(header, payload)

    def __ack_messages(self):
        if self.current_fetch_count > 0:
            self.joiner.write_checkpoints()
            self.recv_queue.ack_all()
            self.current_fetch_count = 0

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
            self.next_stage_queues.send_to_queues(
                msg, queues_suscripted(header, self.name_next_stage_queues)
            )

    def __last_trip_arrived(self, body):
        self.joiner.delete_client(get_id_client(body))
        self.em_queue.send(ack_msg(body, self.id_worker))

    def stop(self, *args):
        if self.running:
            self.running = False
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )
