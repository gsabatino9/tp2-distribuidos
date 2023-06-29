from collections import namedtuple
from struct import pack, unpack, calcsize


def decode(header_bytes):
    return MessageEOF.decode(header_bytes)


def eof_msg(header):
    return MessageEOF(MessageEOF.EOF, header.id_client).encode()


def eof_msg_from_id(id_client):
    return MessageEOF(MessageEOF.EOF, id_client).encode()


def is_eof(header):
    return header.msg_type == MessageEOF.EOF


def ack_msg(header_bytes, id_worker):
    id_client = get_id_client(header_bytes)
    return MessageEOF.ack(id_client, id_worker)


def get_id_client(header_bytes):
    header = decode(header_bytes)
    return header.id_client


class MessageEOF:
    MSG_CODE = 2

    # msg type
    EOF = 0
    ACK = 1

    HEADER_CODE = "!BBQ20s"
    SIZE_HEADER = calcsize(HEADER_CODE)

    Header = namedtuple("Header", "msg_code msg_type id_client id_worker")

    def __init__(self, msg_type, id_client, id_worker=""):
        self.header = self.Header(self.MSG_CODE, msg_type, id_client, id_worker.encode())

    def encode(self):
        return pack(self.HEADER_CODE, *self.header)

    @classmethod
    def eof(cls, id_client, id_worker=""):
        return cls(cls.EOF, id_client, id_worker).encode()

    @classmethod
    def ack(cls, id_client, id_worker=""):
        return cls(cls.ACK, id_client, id_worker).encode()

    @staticmethod
    def decode(header_bytes):
        return MessageEOF.Header._make(unpack(MessageEOF.HEADER_CODE, header_bytes))
