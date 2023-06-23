from protocol.message_client import MessageClient


def is_eof(header):
    return header.msg_type == MessageClient.SEND_LAST


def is_get_id(header):
    return header.msg_type == MessageClient.GET_ID
