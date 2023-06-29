from protocol.message_client import MessageClient
from protocol.message_server import MessageServer
from server.common.utils_messages_eof import MessageEOF
from server.common.utils_messages_group import MessageGroup
from server.common.utils_messages_new_client import (
    MessageNewClient,
    MessageStatusSession,
)
from server.common.utils_messages_results import MessageResults


def is_message_client(msg_bytes):
    return msg_bytes[0] == MessageClient.MSG_CODE


def is_message_server(msg_bytes):
    return msg_bytes[0] == MessageServer.MSG_CODE


def is_message_eof(msg_bytes):
    return msg_bytes[0] == MessageEOF.MSG_CODE


def is_message_new_client(msg_bytes):
    return msg_bytes[0] == MessageNewClient.MSG_CODE


def is_message_status_session(msg_bytes):
    return msg_bytes[0] == MessageStatusSession.MSG_CODE


def is_message_results(msg_bytes):
    return msg_bytes[0] == MessageResults.MSG_CODE
