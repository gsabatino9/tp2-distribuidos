import signal, sys
from server.common.queue.connection import Connection
from server.filters.common.filter import Filter
from server.common.utils_messages_client import (
    decode,
    construct_msg,
    customer_subscribed_to_query,
)
from server.common.utils_messages_eof import ack_msg
from server.common.utils_messages import is_message_eof
from server.common.keep_alive.keep_alive import KeepAlive


class FilterController:
    def __init__(
        self,
        id_query,
        name_recv_queue,
        name_em_queue,
        node_to_send_trips,
        columns_names,
        reduced_columns,
        func_filter,
    ):
        self.__init_filter(
            id_query,
            columns_names,
            reduced_columns,
            func_filter,
            name_recv_queue,
        )
        self.__connect(name_recv_queue, name_em_queue, node_to_send_trips)
        self.__run()

    def __init_filter(
        self,
        id_query,
        columns_names,
        reduced_columns,
        func_filter,
        name_recv_queue,
    ):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.id_query = id_query
        self.not_filtered = 0
        self.filter = Filter(columns_names, reduced_columns, func_filter)
        self.keep_alive = KeepAlive()
        self.id_worker = name_recv_queue
        print("action: filter_started | result: success")

    def __connect(self, name_recv_queue, name_em_queue, node_to_send_trips):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.basic_queue(name_recv_queue)
            queue_name, size_node = node_to_send_trips
            self.send_queue = self.queue_connection.sharding_queue(
                queue_name, size_node, 1
            )

            self.em_queue = self.queue_connection.pubsub_queue(name_em_queue)
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def __run(self):
        """
        start receiving messages.
        """
        self.keep_alive.start()
        self.recv_queue.receive(self.proccess_message)
        try:
            self.queue_connection.start_receiving()
        except:
            if self.running:
                raise  # gracefull quit
        self.keep_alive.stop()
        self.keep_alive.join()

    def proccess_message(self, body):
        if is_message_eof(body):
            self.__eof_arrived(body)
        else:
            self.__trips_arrived(body)

    def __trips_arrived(self, body):
        header, joined_trips = decode(body)

        if customer_subscribed_to_query(header, self.id_query):
            trips_to_next_stage = self.__filter_trips(joined_trips)
            self.__send_to_next_stage(header, trips_to_next_stage)

    def __filter_trips(self, trips):
        """
        filters each trip that does not meet the condition.
        """
        trips_to_next_stage = []

        for trip in trips:
            new_trip = self.filter.apply(trip)
            if new_trip:
                self.not_filtered += 1
                trips_to_next_stage.append(new_trip)

        return trips_to_next_stage

    def __send_to_next_stage(self, header, trips_to_next_stage):
        if len(trips_to_next_stage) > 0:
            msg = construct_msg(header, trips_to_next_stage)
            self.send_queue.send_static(msg, header.id_client)

    def __eof_arrived(self, body):
        self.em_queue.send(ack_msg(body, self.id_worker))
        print(f"action: eof_trips_arrived | not_filtered_trips: {self.not_filtered}")

    def stop(self, *args):
        if self.running:
            self.running = False
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )
