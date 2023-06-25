import signal, sys
from server.common.queue.connection import Connection
from server.appliers.common.applier import Applier
from server.common.utils_messages_eof import ack_msg
from server.common.utils_messages_group import decode, is_eof, construct_msg


class ApplierController:
    def __init__(
        self,
        name_recv_queue,
        name_em_queue,
        name_send_queue,
        id_query,
        operation,
        gen_result_msg,
    ):
        self.__init_applier(str(id_query), gen_result_msg, operation)

        self.__connect(name_recv_queue, name_em_queue, name_send_queue)
        self.__run()

    def __init_applier(self, id_query, gen_result_msg, operation):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.id_query = id_query
        self.gen_result_msg = gen_result_msg
        self.applier = Applier(operation)

        print("action: applier_started | result: success")

    def __connect(self, name_recv_queue, name_em_queue, name_send_queue):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.basic_queue(name_recv_queue)
            self.send_queue = self.queue_connection.routing_queue(name_send_queue)

            self.em_queue = self.queue_connection.pubsub_queue(name_em_queue)
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def __run(self):
        """
        start receiving messages.
        """
        self.recv_queue.receive(self.process_messages)
        try:
            self.queue_connection.start_receiving()
        except Exception as e:
            if self.running:
                print(f"action: middleware_error | error: {str(e)}")
        except:
            if self.running:
                print(f"action: middleware_error | error: unknown.")


    def process_messages(self, ch, method, properties, body):
        if is_eof(body):
            self.__eof_arrived(ch, body)
        else:
            self.__agroup_trips_arrived(body)

    def __agroup_trips_arrived(self, body):
        header, agrouped_trips = decode(body)

        result_trips = self.__apply_condition_to_agrouped_trips(agrouped_trips)
        self.__send_result(header.id_client, result_trips)

    def __apply_condition_to_agrouped_trips(self, agrouped_trips):
        """
        saves each data that satisfies the condition.
        Two things can happen:
        1. The applier consists of applying an operation (such as mean), in which case all the data satisfies it.
        2. The applier has a condition, such as one parameter being double the other.
        """
        result_trips = []

        for trip in agrouped_trips:
            trip = trip.split(",")
            try:
                result, msg_to_send = self.gen_result_msg(trip, self.applier)
                if result:
                    result_trips.append(msg_to_send)
            except:
                print("action: ignore_trip | msg: invalid or empty trip arrived")

        return result_trips

    def __send_result(self, id_client, trips_to_next_stage):
        if len(trips_to_next_stage) > 0:
            msg = construct_msg(id_client, trips_to_next_stage)
            self.send_queue.send(msg, routing_key=self.id_query)

    def __eof_arrived(self, ch, body):
        self.em_queue.send(ack_msg(body))
        print("action: eof_trips_arrived")

    def stop(self, *args):
        if self.running:
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )

            self.running = False
