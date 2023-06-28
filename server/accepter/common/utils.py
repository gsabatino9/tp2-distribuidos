from protocol.message_client import MessageClient


def is_eof(header):
    return header.msg_type == MessageClient.SEND_LAST


def is_init_session(header):
    return header.msg_type == MessageClient.INIT_SESSION
