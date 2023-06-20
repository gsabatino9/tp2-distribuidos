from protocol.communication import Communication
from protocol.message_client import MessageClient
from protocol.message_server import MessageServer


class CommunicationServer:
    """
    A class that represents a server-side communication channel.
    """

    CHUNK_SIZE = 100

    def __init__(self, socket):
        """
        Constructs a CommunicationServer object.

        :param socket: The socket object used for communication.
        """
        self.comm = Communication(socket)

    def getpeername(self):
        return self.comm.getpeername()

    def send_id_client(self, id_client):
        msg = MessageServer.id_client_message(id_client)
        self.comm.send_message(msg)

    def send_ack_batch(self, id_batch):
        msg = MessageServer.batch_received_message(id_batch)
        self.comm.send_message(msg)

    def send_results(self, msg, is_last=False):
        if is_last:
            msg = MessageServer.last_chunk_message()
        self.comm.send_message(msg)

    def send_error_message(self, id_client):
        msg = MessageServer.error_message(id_client)
        self.comm.send_message(msg)

    def recv_data(self, decode_payload=True):
        """
        Receives a message from the client and decodes it.

        :return: The decoded header and payload of the message.
        """
        header = self.__recv_header()
        payload = self.__recv_payload(header.len, decode_payload)

        return header, payload

    def __recv_header(self):
        """
        Receives a message header from the client and decodes it.

        :return: The decoded header of the message.
        """
        header = self.comm.recv_header(MessageClient.SIZE_HEADER)
        header = MessageClient.decode_header(header)

        return header

    def __recv_payload(self, len_payload, decode_payload=True):
        """
        Receives a message payload from the client and decodes it.

        :param len_payload: The length of the payload to be received.
        :return: The decoded payload of the message.
        """
        payload = self.comm.recv_payload(len_payload)
        if decode_payload:
            payload = MessageClient.decode_payload(payload)

        return payload

    def stop(self):
        """
        Closes the communication channel.
        """
        self.comm.stop()
