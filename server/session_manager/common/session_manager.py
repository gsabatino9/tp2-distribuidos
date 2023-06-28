import signal, sys
from datetime import datetime
from server.common.utils_messages_new_client import (
    error_message,
    assigned_id_message,
    decode_msg_session,
    is_request_session,
    is_eof_sent
)
from server.common.queue.connection import Connection
from server.common.keep_alive.keep_alive import KeepAlive
from common.state import SessionManagerState


class SessionManager:
    def __init__(
        self, max_clients, name_recv_queue, name_send_queue, name_end_session_queue
    ):
        self.__init_session_manager(max_clients)
        self.__connect_queue(name_recv_queue, name_send_queue, name_end_session_queue)

    def __init_session_manager(self, max_clients):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.max_clients = max_clients
        # self.state = SessionManagerState()
        self.sessions = []
        self.keep_alive = KeepAlive()
        print("action: session_manager_started | result: success")

    def __connect_queue(self, name_recv_queue, name_send_queue, name_end_session_queue):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.pubsub_queue(
                name_recv_queue,
                # auto_ack=False
            )
            self.send_queue = self.queue_connection.pubsub_queue(name_send_queue)
            self.end_session_queue = self.queue_connection.pubsub_queue(
                name_end_session_queue, auto_ack=False
            )
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def run(self):
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

    def process_messages(self, msg_bytes):
        msg = decode_msg_session(msg_bytes)
        if is_request_session(msg):
            self.init_session(msg.id_client)
        elif is_eof_sent(msg):
            self.eof_sent(msg.id_client)
        else:
            self.end_session(msg.id_client)

    def init_session(self, id_client):
        #self.__verify_timestamps()

        print(f"action: new_session_request | id_client: {id_client}")
        if self.__server_not_full(id_client):
            self.sessions.append(
                # id_client     timestamp               is_deleting_client
                (id_client, self.__get_timestamp(), False)
            )

            msg = assigned_id_message(id_client)
            print(f"action: request_session | result: success | id_client: {id_client}")
        else:
            msg = error_message(id_client)
            print("action: request_session | result: failure")

        # self.state.write_checkpoint()
        # self.recv_queue.ack_all()
        self.send_queue.send(msg)

    def __server_not_full(self, id_client):
        # TODO: verificar si el cliente está
        return len(self.sessions) < self.max_clients

    def __get_timestamp(self):
        dt = datetime.now()
        return datetime.timestamp(dt)

    def end_session(self, id_client):
        client_address = body
        if id_client := self.state.delete_client(client_address):
            print(f"action: end_session | result: success | id_client: {id_client}")

        self.state.write_checkpoint()
        self.end_session_queue.ack_all()

    def stop(self, *args):
        if self.running:
            self.running = False

            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )
