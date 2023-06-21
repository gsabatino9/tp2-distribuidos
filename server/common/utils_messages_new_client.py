from collections import namedtuple
from struct import pack, unpack


def error_message(client_address):
    return MessageNewClient(MessageNewClient.Error, 0, client_address).encode()


def assigned_id_message(id_client, client_address):
    return MessageNewClient(
        MessageNewClient.ASSIGNED_ID, id_client, client_address
    ).encode()


def decode(msg):
    msg = MessageNewClient.decode(msg)
    id_client = msg.id_client
    client_address = msg.client_address.decode().split('\0')[0]

    return id_client, client_address


class MessageNewClient:
    # msg types
    ASSIGNED_ID = 0
    ERROR = 1

    # Struct format for message header
    HEADER_CODE = "!BQ20s"
    # Size of header in bytes

    # Define the named tuples used in the protocol
    Header = namedtuple("Header", "msg_type id_client client_address")

    def __init__(self, msg_type, id_client, client_address):
        self.header = self.Header(msg_type, id_client, client_address)

    def encode(self):
        return pack(self.HEADER_CODE, *self.header)

    @staticmethod
    def decode(msg):
        return MessageNewClient.Header._make(unpack(MessageNewClient.HEADER_CODE, msg))
