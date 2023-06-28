import csv, socket, time, signal, sys, struct
from itertools import islice
from datetime import datetime, timedelta
from protocol.communication_client import CommunicationClient
from common.utils import (
    construct_payload,
    is_eof,
    is_id_client,
    get_id_client,
    is_error,
)
from common.middleware_communication import connect


class Client:
    def __init__(self, addresses, chunk_size, max_retries, id_client, suscriptions):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.addresses = addresses
        self.id_client = id_client
        self.suscriptions = suscriptions
        self.chunk_size = chunk_size
        self.max_retries = max_retries

    def __connect(self, host, port):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((host, port))
        self.conn = CommunicationClient(client_socket, self.suscriptions)

        print(
            f"action: client_connected | result: success | addr: {self.conn.getpeername()} | suscriptions: {self.suscriptions}"
        )

    def run(self, filepath, types_files, addr_consult):
        self.conn = connect(self.addresses, self.id_client, self.suscriptions)
        self.__init_session()
        self.__send_files(filepath, types_files)
        self.__get_results(addr_consult)

    def __init_session(self):
        session_accepted = False
        while not session_accepted:
            self.conn.send_init_session()
            session_accepted = self.conn.recv_status_session()
            if session_accepted:
                print(
                    f"action: id_client_received | result: success | id_client: {self.id_client}"
                )
            else:
                print(
                    f"action: id_client_received | result: failure | msg: retrying in 1sec"
                )
                time.sleep(1)

    def __send_files(self, filepath, types_files):
        for file in types_files:
            self.__send_type_file(filepath, file)
        self.__send_last(types_files[-1])

        print(f"action: ack_files | result: success | msg: all files sent to server")
        self.conn.stop()

    def __send_type_file(self, filepath, type_file):
        """
        it sends all the files of the same type (stations, weather, trips).
        """
        send_data = 0

        with open(filepath + type_file + ".csv", newline="") as csvfile:
            reader = csv.reader(csvfile, delimiter=",")
            # skip header
            next(reader)
            send_data += self.__send_file_in_chunks(type_file, reader)

        print(
            f"action: file_sent | result: success | type_file: {type_file} | amount_chunks: {send_data}"
        )

    def __send_file_in_chunks(self, type_file, reader):
        """
        it sends a file with grouped rows (chunk).
        """
        send_data = 0

        while True:
            chunk = list(islice(reader, self.chunk_size))
            if not chunk:
                break
            chunk = self.__preprocess_chunk(type_file, chunk)
            self.__send_chunk(type_file, chunk, False)
            send_data += 1

        return send_data

    def __send_last(self, type_file):
        self.__send_chunk(type_file, list(""), True)

    def __send_chunk(self, data_type, chunk, last_chunk):
        payload = construct_payload(chunk)
        self.conn.send(data_type, payload, last_chunk)

        self.__recv_ack_chunk()

    def __recv_ack_chunk(self):
        self.conn.recv_ack()

    def __preprocess_chunk(self, type_file, chunk):
        if type_file == "trips":
            return self.__preprocess_trips(chunk)
        elif type_file == "weather":
            return self.__preprocess_weather(chunk)
        else:
            return chunk

    def __preprocess_trips(self, chunk):
        for row in chunk:
            start_date = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S")
            end_date = datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S")
            row[0] = start_date.strftime("%Y-%m-%d")
            row[2] = end_date.strftime("%Y-%m-%d")

        return chunk

    def __preprocess_weather(self, chunk):
        for row in chunk:
            date_aux = datetime.strptime(row[0], "%Y-%m-%d")
            new_date = date_aux - timedelta(days=1)
            row[0] = new_date.strftime("%Y-%m-%d")

        return chunk

    def __get_results(self, addr_consult):
        results = {i: [] for i in self.suscriptions}
        ended = False
        while not ended:
            try:
                self.__connect_with_consults_server(addr_consult[0], addr_consult[1])
                while True:
                    header, payload = self.conn.recv_results()
                    if is_eof(header):
                        break
                    else:
                        results[header.id_query].append(payload.data)

                ended = True
            except:
                print(
                    f"action: results_obtained | result: failure | msg: retrying in 1sec"
                )
                time.sleep(1)

        print(f"action: results_obtained | result: success | results: {results}")
        self.__save_results(results)

    def __send_request_results(self):
        self.conn.send_get_results()

    def __connect_with_consults_server(self, host, port):
        self.__connect(host, port)
        self.conn.set_id_client(self.id_client)
        print("action: connection_consult_server | result: success")
        self.__send_request_results()

    def __save_results(self, results):
        """
        it persists the results of the queries in a file.
        """
        with open(f"results/output-client-{self.id_client}.csv", "w", newline="") as f:
            writer = csv.writer(f)
            for key, values in results.items():
                for row in values:
                    for value in row:
                        writer.writerow([key] + [value])

    def stop(self, *args):
        if self.running:
            if hasattr(self, "conn"):
                self.conn.stop()
                print("action: close_resource | result: success | resource: connection")

            self.running = False
