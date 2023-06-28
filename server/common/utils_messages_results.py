from collections import namedtuple
from struct import pack, unpack


def request_message(id_client_handler, id_client):
    return MessageResults(
        MessageResults.REQUEST_RESULTS, id_client_handler, id_client
    ).encode()


def is_error(message_bytes):
    try:
        msg = MessageResults.decode(message_bytes)
        return MessageResults.ERROR == msg.code
    except:
        return False


def error_message():
    return MessageResults(MessageResults.ERROR, 0, 0).encode()


def decode_request_results(message_bytes):
    msg = MessageResults.decode(message_bytes)
    return msg.id_client_handler, msg.id_client


def decode_delete_client(message_bytes):
    msg = MessageResults.decode(message_bytes)
    return msg.id_client


def delete_message(id_client):
    return MessageResults(MessageResults.DELETE_CLIENT, 0, id_client).encode()


def is_delete_message(message_bytes):
    try:
        msg = MessageResults.decode(message_bytes)
        return MessageResults.DELETE_CLIENT == msg.code
    except:
        return False


class MessageResults:
    # msg types
    REQUEST_RESULTS = 0
    ERROR = 1
    DELETE_CLIENT = 2

    HEADER_CODE = "!BBQ"
    Header = namedtuple("Header", "code id_client_handler id_client")

    def __init__(self, code, id_client_handler, id_client):
        self.header = self.Header(code, id_client_handler, id_client)

    def encode(self):
        return pack(self.HEADER_CODE, *self.header)

    @staticmethod
    def decode(msg):
        return MessageResults.Header._make(unpack(MessageResults.HEADER_CODE, msg))
