from collections import namedtuple
from struct import pack, unpack


def error_message(id_client):
    return MessageNewClient(MessageNewClient.ERROR, id_client).encode()


def assigned_id_message(id_client):
    return MessageNewClient(MessageNewClient.ASSIGNED_ID, id_client).encode()


def decode_reply(msg_bytes):
    msg = MessageNewClient.decode(msg_bytes)
    return msg.id_client, msg.msg_type == MessageNewClient.ASSIGNED_ID


class MessageNewClient:
    # msg types
    ASSIGNED_ID = 0
    ERROR = 1

    # Struct format for message header
    HEADER_CODE = "!BQ"
    # Size of header in bytes

    # Define the named tuples used in the protocol
    Header = namedtuple("Header", "msg_type id_client")

    def __init__(self, msg_type, id_client):
        self.header = self.Header(msg_type, id_client)

    def encode(self):
        return pack(self.HEADER_CODE, *self.header)

    @staticmethod
    def decode(msg):
        return MessageNewClient.Header._make(unpack(MessageNewClient.HEADER_CODE, msg))


def request_init_session(id_client):
    return MessageStatusSession(MessageStatusSession.INIT_SESSION, id_client).encode()


def decode_msg_session(msg):
    return MessageStatusSession.decode(msg)


class MessageStatusSession:
    INIT_SESSION = 0
    EOF_SENT = 1
    DELETE_CLIENT = 2

    # Struct format for message header
    HEADER_CODE = "!BQ"
    # Size of header in bytes

    # Define the named tuples used in the protocol
    Header = namedtuple("Header", "msg_type id_client")

    def __init__(self, msg_type, id_client):
        self.header = self.Header(msg_type, id_client)

    def encode(self):
        return pack(self.HEADER_CODE, *self.header)

    @staticmethod
    def decode(msg):
        return MessageStatusSession.Header._make(
            unpack(MessageStatusSession.HEADER_CODE, msg)
        )

def is_request_session(header):
    return header.msg_type == MessageStatusSession.INIT_SESSION

def is_eof_sent(header):
    return header.msg_type == MessageStatusSession.EOF_SENT
