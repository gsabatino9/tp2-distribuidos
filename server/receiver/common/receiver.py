import socket, signal, sys, queue
from threading import Thread, Lock
from protocol.communication_server import CommunicationServer
from server.common.queue.connection import Connection
from common.utils import is_eof
from common.receiver_ids import ReceiverIds
from server.common.utils_messages_eof import eof_msg
from server.common.utils_messages_client import is_station, is_weather, encode_header
from server.common.utils_messages_status import id_client_msg
from server.common.keep_alive.keep_alive import KeepAlive


class Receiver:
    def __init__(
        self,
        host,
        port,
        name_stations_queue,
        name_weather_queue,
        name_trips_queues,
        name_em_queue,
        name_status_queue,
        name_session_manager_queue,
        name_recv_ids_queue,
        amount_queries,
        max_clients=5,
    ):
        self.__init_receiver(
            amount_queries, host, port, max_clients, name_recv_ids_queue
        )

        self.__connect_queue(
            name_stations_queue,
            name_weather_queue,
            name_trips_queues,
            name_session_manager_queue,
        )
        self.__connect_eof_manager_queue(name_em_queue)
        self.__connect_status_queue(name_status_queue)

    def __init_receiver(
        self, amount_queries, host, port, max_clients, name_recv_ids_queue
    ):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.amount_queries = amount_queries
        self.accepter_socket = self.__create_socket(host, port)
        self.clients_connections = {}
        self.lock_clients_connections = Lock()
        self.max_clients = max_clients
        self.recv_ids = ReceiverIds(
            name_recv_ids_queue, self.clients_connections, self.lock_clients_connections
        )
        self.keep_alive = KeepAlive()
        print("action: receiver_started | result: success")

    def __connect_queue(
        self,
        name_stations_queue,
        name_weather_queue,
        name_trips_queues,
        name_session_manager_queue,
    ):
        try:
            self.queue_connection = Connection()
            self.stations_queue = self.queue_connection.basic_queue(name_stations_queue)
            self.weather_queue = self.queue_connection.basic_queue(name_weather_queue)
            self.trips_queues = [
                self.queue_connection.basic_queue(q) for q in name_trips_queues
            ]
            self.session_manager_queue = self.queue_connection.pubsub_queue(
                name_session_manager_queue
            )
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def __connect_eof_manager_queue(self, name_em_queue):
        self.em_queue = self.queue_connection.pubsub_queue(name_em_queue)

    def __connect_status_queue(self, name_status_queue):
        self.status_queue = self.queue_connection.pubsub_queue(name_status_queue)

    def __create_socket(self, host, port):
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.bind((host, port))

        return skt

    def run(self):
        self.keep_alive.start()
        self.recv_ids.start()
        self.accepter_socket.listen(self.max_clients)
        print(f"action: waiting_clients | result: success")

        self.clients_threads = []
        while self.running:
            client_address = self.__accept_client()
            client_thread = Thread(target=self.__handle_client, args=(client_address,))
            client_thread.start()
            self.clients_threads.append(client_thread)

        for client_thread in self.clients_threads:
            client_thread.join()

        self.recv_ids.join()
        self.keep_alive.stop()
        self.keep_alive.join()

    def __accept_client(self):
        client_socket, _ = self.accepter_socket.accept()
        client_connection = CommunicationServer(client_socket)
        client_address = client_connection.getpeername()[0]

        with self.lock_clients_connections:
            self.clients_connections[client_address] = (
                queue.Queue(),
                client_connection,
            )

        print(
            f"action: client_connected | result: success | msg: starting to receive data | client_address: {client_address}"
        )

        # TODO: ver si moverlo al hilo específico del cliente
        self.session_manager_queue.send(client_address)

        return client_address

    def __handle_client(self, client_address):
        not_assigned = self.__assign_id_to_client(client_address)
        if not_assigned:
            print(f"action: close_client | msg: max clients in system")
            self.__close_client(client_address)
        else:
            self.__run_loop_client(client_address)

    def __assign_id_to_client(self, client_address):
        self.lock_clients_connections.acquire()
        queue_client, client_connection = self.clients_connections[client_address]
        self.lock_clients_connections.release()

        id_client = queue_client.get()
        if id_client == 0:
            return True
        else:
            client_connection.send_id_client(id_client)
            return False

    def __close_client(self, client_address):
        # TODO: borrar cola y conexión del cliente acá.
        # Por ahora no es necesario.
        with self.lock_clients_connections:
            _, client_connection = self.clients_connections[client_address]
            client_connection.stop()

    def __run_loop_client(self, client_address):
        types_ended = set()

        with self.lock_clients_connections:
            _, client_connection = self.clients_connections[client_address]

        while len(types_ended) < self.amount_queries:
            header, payload_bytes = client_connection.recv_data(decode_payload=False)

            if is_eof(header):
                types_ended.add(header.data_type)
                self.__send_eof(header)
            else:
                self.__route_message(header, payload_bytes)

            # después de poner el msg en la cola, le mando ack
            self.__send_ack_client(header.id_batch, client_connection)

    def __send_eof(self, header):
        self.em_queue.send(eof_msg(header))

    def __route_message(self, header, payload_bytes):
        """
        send the message according to the type of header.
        """
        msg = encode_header(header) + payload_bytes

        if is_station(header):
            self.stations_queue.send(msg)
        elif is_weather(header):
            self.weather_queue.send(msg)
        else:
            self.__send_msg_to_trips(msg)

    def __send_msg_to_trips(self, msg):
        [trips_queue.send(msg) for trips_queue in self.trips_queues]

    def __send_ack_client(self, id_batch, client_connection):
        """
        informs the client that bach with id_batch arrived successfully.
        """
        client_connection.send_ack_batch(id_batch)

    def stop(self, *args):
        if self.running:
            self.queue_connection.close()
            self.recv_ids.stop()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )
            if hasattr(self, "clients_connections"):
                for _, client_connection in self.clients_connections.values():
                    # TODO: try-catch
                    try:
                        client_connection.stop()
                        print(
                            "action: close_resource | result: success | resource: client_connection"
                        )
                    except:
                        # ya fue cerrada antes la conexión
                        pass

            self.running = False

        
