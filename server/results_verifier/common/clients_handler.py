from multiprocessing import Process
import socket
from protocol.communication_server import CommunicationServer

class ClientsHandler:
    def __init__(self, address, lock, queries_ended, queries_results, max_clients=5):
        self.running = True

        self.accepter_socket = self.__create_socket(address)
        self.lock = lock
        self.queries_ended = queries_ended
        self.queries_results = queries_results
        self.max_clients = max_clients

    def __create_socket(self, address):
        skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        skt.bind(address)

        return skt

    def run(self):
        self.process_loop = Process(target=self.__run_accepter_loop, args=())
        self.process_loop.start()

    def __run_accepter_loop(self):
        self.accepter_socket.listen(self.max_clients)
        print(f"action: waiting_clients | result: success")

        while self.running:
            client_connection = self.__accept_client()
            process = Process(
                target=self.__handle_client, args=(client_connection,)
            )
            process.start()

        self.accepter_socket.close()

    def __accept_client(self):
        client_socket, client_address = self.accepter_socket.accept()
        client_connection = CommunicationServer(client_socket)
        #self.clients_connections[client_address] = client_connection

        print(
            f"action: client_connected | result: success | msg: starting to receive data"
        )

        return client_connection

    def __handle_client(self, client_connection):
        header, _ = client_connection.recv_data(decode_payload=False)
        results_ready = self.__verify_results(header.id_client)

        while not results_ready:
            self.__send_not_ready(client_connection, header.id_client)
            header, _ = client_connection.recv_data(decode_payload=False)
            results_ready = self.__verify_results(header.id_client)

        self.__send_results(client_connection, header.id_client)

    def __verify_results(self, id_client):
        client_results_ready = True
        client_in_queries = False
        
        self.lock.acquire()
        for query, result_ready in self.queries_ended.items():
            if query[0] == id_client:
                client_in_queries = True
                if result_ready:
                    client_results_ready = False
        self.lock.release()

        return client_results_ready and client_in_queries

    def __send_not_ready(self, client_connection, id_client):
        client_connection.send_error_message(id_client)

    def __send_results(self, client_connection, id_client):
        print("enviando resultados")
        self.lock.acquire()
        for query, results in self.queries_results.items():
            if query[0] == id_client:
                if len(results) > 0:
                    client_connection.send_results(query[1], results)
        self.lock.release()
        print("resultados enviados")

    def stop(self, *args):
        if self.running:
            self.accepter_socket.close()
            print(
                "action: close_resource | result: success | resource: accepter_socket"
            )
            self.running = False