import signal, sys
from server.common.queue.connection import Connection
from server.groupby.common.state_manager import StateManager
from server.common.utils_messages_client import decode
from server.common.utils_messages_eof import ack_msg, get_id_client, is_abort_decode
from server.common.utils_messages_group import construct_msg
from server.common.keep_alive.keep_alive import KeepAlive
from server.common.utils_messages import is_message_eof


class GroupbyController:
    def __init__(
        self,
        name_recv_queue,
        name_em_queue,
        name_send_queue,
        size_workers_send,
        operation,
        base_data,
        gen_key_value,
        chunk_size,
    ):
        self.__init_groupby(
            chunk_size,
            operation,
            base_data,
            gen_key_value,
            size_workers_send,
            name_recv_queue,
        )
        self.__connect(
            name_recv_queue, name_em_queue, name_send_queue, size_workers_send
        )
        self.__run()

    def __init_groupby(
        self,
        chunk_size,
        operation,
        base_data,
        gen_key_value,
        size_workers_send,
        name_recv_queue,
    ):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.chunk_size = chunk_size
        self.state = StateManager(operation, base_data)
        self.current_fetch_count = 0
        self.prefetch_limit = 1000
        self.size_workers_send = size_workers_send
        self.gen_key_value = gen_key_value
        self.keep_alive = KeepAlive()
        self.id_worker = name_recv_queue
        print("action: groupby_started | result: success")

    def __connect(
        self, name_recv_queue, name_em_queue, name_send_queue, size_workers_send
    ):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.basic_queue(
                name_recv_queue, auto_ack=False
            )
            self.send_queue = self.queue_connection.multiple_queues(
                [name_send_queue], [self.size_workers_send]
            )

            self.em_queue = self.queue_connection.basic_queue(name_em_queue)
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
                raise  # gracefull quit # gracefull quit

        self.keep_alive.stop()
        self.keep_alive.join()

    def process_messages(self, body):
        # TODO: evaluate if it's a good idea to use 80~90% of the prefetch limit.
        # I (Lucho) added this because i was getting off-by-one errors and just
        # wanted to get it working fast.
        if self.current_fetch_count * 10 // 8 > self.prefetch_limit:
            self.__ack_messages()

        self.current_fetch_count += 1
        if is_message_eof(body):
            self.__eof_arrived(body)
            self.__ack_messages()
        else:
            self.__data_arrived(body)

    def __ack_messages(self):
        self.state.write_checkpoints()
        self.recv_queue.ack_all()
        self.current_fetch_count = 0

    def __data_arrived(self, body):
        header, filtered_trips = decode(body)

        if self.state.is_batch_already_processed(header.id_client, header.id_batch):
            print(
                f"action: data_arrived | result: batch_already_processed | batch_id: {header.id_batch}"
            )
            return

        for trip in filtered_trips:
            trip = trip.split(",")
            self.__agroup_trip(header.id_client, trip)

        self.state.mark_batch_as_processed(header.id_client, header.id_batch)

    def __agroup_trip(self, id_client, trip):
        """
        agroup the trip by the key and store the value that
        generates gen_key_value custom function.
        """
        key, value = self.gen_key_value(trip)
        self.state.add_data(id_client, key, value)

    def __eof_arrived(self, body):
        id_client = get_id_client(body)
        print("action: eof_trips_arrived")

        if not is_abort_decode(body):
            self.__send_to_apply(id_client)

        self.__delete_client(id_client)
        self.em_queue.send(ack_msg(body, self.id_worker))

    def __delete_client(self, id_client):
        if self.state.delete_client(id_client):
            print(f"action: delete_client | result: success | id_client: {id_client}")
        else:
            print(
                f"action: delete_client | result: warning | id_client: {id_client} was not found in groupby data"
            )

    def __send_to_apply(self, id_client):
        """
        sends the grouped data.
        build chunk to send each message.
        """
        to_send = []
        id_batch = 0

        for i, key in enumerate(self.state.iter_data(id_client)):
            to_send.append(self.__str_from_key(id_client, key))

            if self.__finish_chunk_to_send(id_client, i, id_batch, to_send):
                id_batch += 1
                to_send = []

    def __finish_chunk_to_send(self, id_client, i, id_batch, to_send):
        """
        stop building the message if the maximum number of data in a chunk has been reached,
        or if is the last data group.
        """
        if (i + 1) % self.chunk_size == 0 or i + 1 == self.state.len_data(id_client):
            msg = construct_msg(id_client, id_batch, to_send)
            self.send_queue.send(msg)

            return True
        return False

    def __str_from_key(self, id_client, key):
        """
        generates the correct format to send the message.
        concatenates the key with all the values.
        """
        value = self.state.get_data(id_client, key)
        to_ret = f"{key},"
        for v in value:
            to_ret += f"{v},"

        return to_ret[: len(to_ret) - 1]

    def stop(self, *args):
        if self.running:
            self.running = False
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )
