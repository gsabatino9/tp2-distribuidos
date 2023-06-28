from collections import namedtuple
from struct import pack, unpack, calcsize


def decode(header_bytes):
    return MessageEOF.decode(header_bytes)


def eof_msg(header):
    return MessageEOF(MessageEOF.EOF, header.data_type, header.id_client).encode()

def eof_msg_from_id(id_client):
    return MessageEOF(MessageEOF.EOF, MessageEOF.TRIP, id_client).encode()

def is_eof(header):
    return header.msg_type == MessageEOF.EOF


def is_station(header):
    return header.data_type == MessageEOF.STATION


def is_weather(header):
    return header.data_type == MessageEOF.WEATHER


def ack_msg(header_bytes):
    id_client = get_id_client(header_bytes)
    return MessageEOF.ack(MessageEOF.TRIP, id_client)


def get_id_client(header_bytes):
    header = decode(header_bytes)
    return header.id_client


class MessageEOF:
    # msg type
    EOF = 0
    ACK = 1

    # data type
    STATION = 0
    WEATHER = 1
    TRIP = 2

    HEADER_CODE = "!BBQ"
    SIZE_HEADER = calcsize(HEADER_CODE)

    Header = namedtuple("Header", "msg_type data_type id_client")

    def __init__(self, msg_type, data_type, id_client):
        self.header = self.Header(msg_type, data_type, id_client)

    def encode(self):
        return pack(self.HEADER_CODE, *self.header)

    @classmethod
    def eof(cls, data_type, id_client):
        return cls(cls.EOF, data_type, id_client).encode()

    @classmethod
    def ack(cls, data_type, id_client):
        return cls(cls.ACK, data_type, id_client).encode()

    @staticmethod
    def decode(header_bytes):
        return MessageEOF.Header._make(unpack(MessageEOF.HEADER_CODE, header_bytes))
