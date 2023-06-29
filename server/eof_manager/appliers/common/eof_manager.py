import signal, sys
from server.common.queue.connection import Connection
from server.common.utils_messages_eof import *
from server.common.utils_messages_status import get_id_client_from_msg
from server.common.keep_alive.keep_alive import KeepAlive
from server.eof_manager.common.state_eof_manager import EofManagerState


class EOFManager:
    def __init__(
        self,
        name_recv_queue,
        name_appliers_queues,
        name_send_queue,
        name_status_queue,
        size_workers,
    ):
        self.__init_eof_manager(size_workers)
        self.__connect(
            name_recv_queue,
            name_appliers_queues,
            name_send_queue,
            name_status_queue,
            size_workers,
        )
        self.__run()

    def __init_eof_manager(self, size_workers):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.size_workers = size_workers
        self.sum_workers = sum(size_workers)
        self.state = EofManagerState("joiners")
        self.keep_alive = KeepAlive()
        print("action: eof_manager_started | result: success")

    def __connect(
        self,
        name_recv_queue,
        name_appliers_queues,
        name_send_queue,
        name_status_queue,
        size_workers,
    ):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.pubsub_queue(
                name_recv_queue, auto_ack=False
            )
            self.appliers_queues = self.queue_connection.multiple_queues(
                name_appliers_queues, self.size_workers
            )
            self.send_queue = self.queue_connection.pubsub_queue(name_send_queue)
            self.status_queue = self.queue_connection.pubsub_queue(name_status_queue)
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def __run(self):
        """
        start receiving messages.
        """
        self.keep_alive.start()
        self.status_queue.receive(self.receive_new_client)
        self.recv_queue.receive(self.receive_msg)
        try:
            self.queue_connection.start_receiving()
        except:
            if self.running:
                raise  # gracefull quit
        self.keep_alive.stop()
        self.keep_alive.join()

    def receive_new_client(self, body):
        id_new_client = get_id_client_from_msg(body)
        print(f"action: new_client | result: success | id_new_client: {id_new_client}")

    def receive_msg(self, body):
        header = decode(body)
        self.state.verify_client(header.id_client)

        if is_eof(header) or is_abort(header):
            self.__send_eofs(header, body)
        else:
            self.__recv_ack_trips(header, body)

    def __send_eofs(self, header, msg):
        """
        it sends EOF to each known worker.
        """
        print(f"action: send_eofs | result: success | msg: eof arrived")
        self.appliers_queues.broadcast(msg)

        self.recv_queue.ack_all()

    def __recv_ack_trips(self, header, body):
        """
        if the number of workers that returned ack reaches the maximum count, it sends EOF to the next stage.
        """
        self.state.add_ack_client(header.id_client, get_id_worker(header))

        if self.state.amount_acks(header.id_client) == self.sum_workers:
            print(
                f"action: close_stage | result: success | id_client: {header.id_client}"
            )
            self.send_queue.send(eof_msg(header))
            self.state.delete_client(header.id_client)

        self.state.write_checkpoint()
        self.recv_queue.ack_all()

    def stop(self, *args):
        if self.running:
            self.running = False
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )
