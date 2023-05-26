from protocol.message_client import MessageClient
from protocol.message_server import MessageServer


def construct_city(city):
    if city == "montreal":
        return MessageClient.MONTREAL
    elif city == "toronto":
        return MessageClient.TORONTO
    else:
        return MessageClient.WASHINGTON


def construct_payload(rows):
    return [",".join(e) for e in rows]


def is_eof(header):
    return header.msg_type == MessageServer.SEND_LAST
