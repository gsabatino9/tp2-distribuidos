from threading import Thread
from server.common.queue.connection import Connection
from server.common.utils_messages_client import is_eof
import time

class ClientHandler(Thread):
    def __init__(self, name_recv_exchange, name_recv_queue, client_connection):
        super().__init__()
        self.name_recv_exchange = name_recv_exchange
        self.name_recv_queue = name_recv_queue

        self.client_connection = client_connection

    def run(self):
        # recv request for info
        print("esperando request")
        header, _ = self.client_connection.recv_data(decode_payload=False)
        print("request recibido: id =", header.id_client)
        time.sleep(5)
        self.__connect_client(header.id_client)
        
        # start receving batches
        print("empezando a recibir batches")
        self.results_queue.receive(self.__process_batch)
        self.queue_connection.start_receiving()

    def __connect_client(self, id_client):
        # TODO: try-catch
        self.queue_connection = Connection()
        self.results_queue = self.queue_connection.routing_build_queue(
            self.name_recv_exchange, self.name_recv_queue, routing_keys=[str(id_client)]
        )

        print("cliente conectado con colas")

    def __process_batch(self, ch, method, properties, body):
        print("procesando batch")
        if is_eof(body):
            self.client_connection.send_results(body, is_last=True)
            self.__stop_connections()
        else:
            self.client_connection.send_results(body, is_last=False)

    def __stop_connections(self):
        self.queue_connection.delete_queue(self.name_recv_queue)
        self.queue_connection.close()
        self.client_connection.stop()