from protocol.message_client import MessageClient
from protocol.message_server import MessageServer


def construct_payload(rows):
    return [",".join(e) for e in rows]


def is_eof(header):
    return header.msg_type == MessageServer.SEND_LAST_RESULT


def is_error(header):
    return header.msg_type == MessageServer.ERROR_MESSAGE
