import signal, sys
from server.common.queue.connection import Connection
from server.common.utils_messages_eof import *


class EOFManager:
    def __init__(self, name_recv_queue, name_groupby_queues, name_send_queue):
        self.__init_eof_manager()
        self.__connect(name_recv_queue, name_groupby_queues, name_send_queue)
        self.__run()

    def __init_eof_manager(self):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.acks = 0

        print("action: eof_manager_started | result: success")

    def __connect(self, name_recv_queue, name_groupby_queues, name_send_queue):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.pubsub_queue(name_recv_queue)
            self.groupby_queues = [
                self.queue_connection.basic_queue(q) for q in name_groupby_queues
            ]
            self.send_queue = self.queue_connection.pubsub_queue(name_send_queue)
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def __run(self):
        """
        start receiving messages.
        """
        self.recv_queue.receive(self.receive_msg)
        self.queue_connection.start_receiving()

    def receive_msg(self, ch, method, properties, body):
        header = decode(body)

        if is_eof(header):
            self.__send_eofs(header, body)
        else:
            self.__recv_ack_trips(header, body)

    def __send_eofs(self, header, msg):
        """
        it sends EOF to each known groupby controller.
        """
        print(f"action: send_eofs | result: success | msg: eof arrived")
        for q in self.groupby_queues:
            q.send(msg)

    def __recv_ack_trips(self, header, body):
        """
        if the number of workers that returned ack reaches the maximum count, it sends EOF to the next stage.
        """
        self.acks += 1

        if self.acks == len(self.groupby_queues):
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
