import signal, sys
from server.common.queue.connection import Connection
from server.filters.common.filter import Filter
from server.common.utils_messages_client import (
    decode,
    is_eof,
    construct_msg,
    customer_subscribed_to_query,
)
from server.common.utils_messages_eof import ack_msg


class FilterController:
    def __init__(
        self,
        id_query,
        name_recv_exchange,
        name_recv_queue,
        name_em_queue,
        name_send_queue,
        columns_names,
        reduced_columns,
        func_filter,
    ):
        self.__init_filter(id_query, columns_names, reduced_columns, func_filter)
        self.__connect(
            name_recv_exchange, name_recv_queue, name_em_queue, name_send_queue
        )
        self.__run()

    def __init_filter(self, id_query, columns_names, reduced_columns, func_filter):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.id_query = id_query
        self.not_filtered = 0
        self.filter = Filter(columns_names, reduced_columns, func_filter)

        print("action: filter_started | result: success")

    def __connect(
        self, name_recv_exchange, name_recv_queue, name_em_queue, name_send_queue
    ):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.pubsub_worker_queue(
                name_recv_exchange, name_recv_queue
            )
            self.send_queue = self.queue_connection.basic_queue(name_send_queue)

            self.em_queue = self.queue_connection.pubsub_queue(name_em_queue)
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def __run(self):
        """
        start receiving messages.
        """
        self.recv_queue.receive(self.proccess_message)
        self.queue_connection.start_receiving()

    def proccess_message(self, ch, method, properties, body):
        if is_eof(body):
            self.__eof_arrived(ch, body)
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
            self.send_queue.send(msg)

    def __eof_arrived(self, ch, body):
        #ch.stop_consuming()
        self.em_queue.send(ack_msg(body))
        print(f"action: eof_trips_arrived | not_filtered_trips: {self.not_filtered}")

    def stop(self, *args):
        if self.running:
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )

            self.running = False

        sys.exit(0)
