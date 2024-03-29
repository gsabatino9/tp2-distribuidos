import socket, signal, sys, threading, queue
from common.results_sender import ResultsSender
from common.state import ResultsVerifierState
from server.common.queue.connection import Connection
from server.common.utils_messages_client import results_message, last_message
from server.common.utils_messages_eof import ack_msg, get_id_client, is_abort_decode
from server.common.utils_messages_group import decode
from server.common.utils_messages import is_message_eof
from server.common.utils_messages_results import (
    decode_request_results,
    error_message,
    is_delete_message,
    decode_delete_client,
)
from server.common.utils_messages_new_client import delete_client
from server.common.keep_alive.keep_alive import KeepAlive


class ResultsVerifier:
    CHUNK_SIZE = 100

    def __init__(
        self,
        address_consult_clients,
        name_recv_queue,
        name_em_queue,
        name_session_manager_queue,
        name_send_exchange,
        name_send_queue,
        amount_queries,
    ):
        self.__init_results_verifier(
            address_consult_clients,
            name_session_manager_queue,
            name_recv_queue,
            name_send_exchange,
            name_send_queue,
            amount_queries,
        )
        self.__connect(
            name_recv_queue,
            name_em_queue,
            name_send_exchange,
            name_send_queue,
            name_session_manager_queue,
            amount_queries,
        )

    def __init_results_verifier(
        self,
        address_consult_clients,
        name_session_manager_queue,
        name_recv_queue,
        name_send_exchange,
        name_send_queue,
        amount_queries,
    ):
        self.running = True
        signal.signal(signal.SIGTERM, self.stop)

        self.state = ResultsVerifierState(amount_queries)
        self.prefetch_limit = 1000
        self.current_fetch_count = 0
        self.client_handlers_queues = [queue.Queue() for i in range(3)]
        self.sender = ResultsSender(
            name_session_manager_queue,
            name_recv_queue,
            address_consult_clients,
            self.client_handlers_queues,
        )
        self.id_worker = name_recv_queue
        self.keep_alive = KeepAlive()
        print("action: results_verifier_started | result: success")

    def __connect(
        self,
        name_recv_queue,
        name_em_queue,
        name_send_exchange,
        name_send_queue,
        name_session_manager_queue,
        amount_queries,
    ):
        try:
            self.queue_connection = Connection()
            self.recv_queue = self.queue_connection.routing_queue(
                name_recv_queue,
                routing_keys=[str(i) for i in range(1, amount_queries + 1)]
                + ["request_results"],
                auto_ack=False,
            )

            self.session_manager_queue = self.queue_connection.basic_queue(
                name_session_manager_queue
            )

            self.em_queue = self.queue_connection.basic_queue(name_em_queue)
            self.send_queue = self.queue_connection.routing_building_queue(
                name_send_exchange, name_send_queue
            )
        except OSError as e:
            print(f"error: creating_queue_connection | log: {e}")
            self.stop()

    def run(self):
        """
        start receiving messages.
        """
        self.keep_alive.start()
        self.sender.start()
        self.recv_queue.receive(
            self.process_messages, prefetch_count=self.prefetch_limit
        )
        try:
            self.queue_connection.start_receiving()
        except:
            if self.running:
                raise  # rethrow ex if not graceful quitting
        self.sender.stop()
        self.sender.join()
        self.keep_alive.stop()
        self.keep_alive.join()

    def process_messages(self, body, id_query):
        self.current_fetch_count += 1
        if self.current_fetch_count * 10 // 8 > self.prefetch_limit:
            self.__ack_messages()
        if id_query == "request_results":
            if is_delete_message(body):
                id_client = decode_delete_client(body)
                self.__delete_client(id_client)
                self.__ack_messages()
            else:
                id_client_handler, id_client = decode_request_results(body)
                self.__verify_client(id_client)

                if self.__verify_last_result(id_client):
                    self.__inform_results(id_client_handler, id_client)
                else:
                    self.__inform_error(id_client_handler)
                self.__ack_messages()
        else:
            id_query = int(id_query)
            if is_message_eof(body):
                print("action: eof_trips_arrived")
                self.__eof_arrived(id_query, body)
                self.__ack_messages()
            else:
                self.__query_result_arrived(body, id_query)

    def __ack_messages(self):
        if self.current_fetch_count > 0:
            self.state.write_checkpoints()
            self.recv_queue.ack_all()
            self.current_fetch_count = 0

    def __query_result_arrived(self, body, id_query):
        """
        stores the results by query.
        """
        header, results = decode(body)

        if self.state.has_batch_been_processed(id_query, id_query, header.id_batch):
            print(
                f"action: data_arrived | result: batch_already_processed | batch_id: {header.id_batch}"
            )
            return

        id_client = header.id_client
        self.__verify_client(id_client)
        self.state.add_results(id_client, id_query, results)

        self.state.mark_batch_as_processed(header.id_client, id_query, header.id_batch)

    def __eof_arrived(self, id_query, body):
        """
        save the finished query and send an acknowledgment to the EOF manager.
        then, check if all the queries have ended or if it needs to continue waiting for the EOF, otherwise.
        """
        id_client = get_id_client(body)
        self.__verify_client(id_client)
        self.em_queue.send(ack_msg(body, self.id_worker))
        self.state.mark_query_as_ended(id_client, id_query)

        self.__verify_last_result(id_client)

        if is_abort_decode(body):
            self.__delete_client(id_client)
            self.session_manager_queue.send(delete_client(id_client))

    def __verify_client(self, id_client):
        if self.state.add_client(id_client):
            print(f"action: add_client | result: success | id_client: {id_client}")

    def __verify_last_result(self, id_client):
        """
        check if all the queries have ended or if it needs to continue waiting for the EOF, otherwise.
        if it finishes, report the results to the client.
        """
        return self.state.verify_last_result(id_client)

    def __inform_results(self, id_client_handler, id_client):
        queue = self.client_handlers_queues[id_client_handler]

        batches_to_send = self.__get_batches_to_send(id_client)
        queue.put(batches_to_send)

        print(f"action: inform_results | result: success | id_client: {id_client}")

    def __inform_error(self, id_client_handler):
        queue = self.client_handlers_queues[id_client_handler]
        queue.put(error_message())
        print(f"action: inform_results | result: failure")

    def __get_batches_to_send(self, id_client):
        results_client = self.__get_results_client(id_client)
        batches_to_send = []
        id_batch = 0

        for id_query, results_query in results_client:
            for result in results_query:
                batch = results_message(id_query, id_batch, result)
                batches_to_send.append(batch)
                id_batch += 1

        return batches_to_send

    def __get_results_client(self, id_client):
        results_client = []
        for id_query, results_query in self.state.get_results(id_client):
            results_client.append(
                (id_query, self.__partition_into_batches(results_query))
            )

        return results_client

    def __partition_into_batches(self, list_batch):
        batches = []
        last = 0
        for i, elem in enumerate(list_batch):
            if (i + 1) % self.CHUNK_SIZE == 0 or i + 1 == len(list_batch):
                batches.append(list_batch[last : i + 1])
                last = i + 1

        return batches

    def __delete_client(self, id_client):
        self.state.delete_client(id_client)
        print(f"action: delete_client | result: success | id_client: {id_client}")

    def stop(self, *args):
        if self.running:
            self.running = False
            self.queue_connection.stop_receiving()
            self.queue_connection.close()
            print(
                "action: close_resource | result: success | resource: rabbit_connection"
            )
