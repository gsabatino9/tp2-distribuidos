import signal, sys
from server.common.queue.connection import Connection
from server.groupby.common.groupby import Groupby
from server.common.utils_messages_client import decode, is_eof
from server.common.utils_messages_eof import ack_msg, get_id_client
from server.common.utils_messages_group import construct_msg


class GroupbyController:
    def __init__(
        self,
        name_recv_queue,
        name_em_queue,
        name_send_queue,
        operation,
        base_data,
        gen_key_value,
        chunk_size,
    ):
        self.__init_groupby(chunk_size, operation, base_data, gen_key_value)
        self.__connect(name_recv_queue, name_em_queue, name_send_queue)
        self.__run()

    def __init_groupby(self, chunk_size, operation, base_data, gen_key_value):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.chunk_size = chunk_size
        self.groupby = Groupby(operation, base_data)
        self.gen_key_value = gen_key_value
        print("action: groupby_started | result: success")

    def __connect(self, name_recv_queue, name_em_queue, name_send_queue):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.basic_queue(name_recv_queue)
            self.send_queue = self.queue_connection.basic_queue(name_send_queue)

            self.em_queue = self.queue_connection.pubsub_queue(name_em_queue)
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
            self.__eof_arrived(body)
        else:
            self.__data_arrived(body)

    def __data_arrived(self, body):
        header, filtered_trips = decode(body)

        for trip in filtered_trips:
            trip = trip.split(",")
            self.__agroup_trip(header.id_client, trip)

    def __agroup_trip(self, id_client, trip):
        """
        agroup the trip by the key and store the value that
        generates gen_key_value custom function.
        """
        key, value = self.gen_key_value(trip)
        self.groupby.add_data(id_client, key, value)

    def __eof_arrived(self, body):
        id_client = get_id_client(body)
        
        self.__send_to_apply(id_client)
        self.__delete_client(id_client)
        self.em_queue.send(ack_msg(body))
        print("action: eof_trips_arrived")

    def __delete_client(self, id_client):
        self.groupby.delete_client(id_client)
        print(f"action: delete_client | result: success | id_client: {id_client}")


    def __send_to_apply(self, id_client):
        """
        sends the grouped data.
        build chunk to send each message.
        """
        to_send = []

        for i, key in enumerate(self.groupby.grouped_data):
            to_send.append(self.__str_from_key(key))

            if self.__finish_chunk_to_send(id_client, i, to_send):
                to_send = []

    def __finish_chunk_to_send(self, id_client, i, to_send):
        """
        stop building the message if the maximum number of data in a chunk has been reached,
        or if is the last data group.
        """
        if (i + 1) % self.chunk_size == 0 or i + 1 == len(self.groupby.grouped_data):
            msg = construct_msg(id_client, to_send)
            self.send_queue.send(msg)

            return True
        else:
            return False

    def __str_from_key(self, key):
        """
        generates the correct format to send the message.
        concatenates the key with all the values.
        """
        value = self.groupby.grouped_data[key]
        to_ret = f"{key[1]},"
        for v in value:
            to_ret += f"{v},"

        return to_ret[: len(to_ret) - 1]

    def stop(self, *args):
        if self.running:
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )

            self.running = False

        sys.exit(0)
