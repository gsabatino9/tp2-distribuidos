from protocol.message_client import MessageClient


def is_eof(header):
    return header.msg_type == MessageClient.SEND_LAST
