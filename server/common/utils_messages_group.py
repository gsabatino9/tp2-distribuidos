from collections import namedtuple
from struct import pack, unpack, calcsize


def construct_msg(grouped_trips):
    return MessageGroup(1, grouped_trips).encode()


def decode(body):
    header, trips_group_array = MessageGroup.decode(body)
    return header, trips_group_array[0]


def is_eof(body):
    try:
        decode(body)
        return False
    except:
        return True


class MessageGroup:
    # Struct format for message header
    HEADER_CODE = "!BI"
    # Size of header in bytes
    SIZE_HEADER = calcsize(HEADER_CODE)

    # Define the named tuples used in the protocol
    Header = namedtuple("Header", "num_query len")
    Payload = namedtuple("Payload", "data")

    def __init__(self, num_query, payload):
        if payload is None:
            payload = []
        payload_bytes = self._pack_payload(payload)

        self.header = self.Header(num_query, len(payload_bytes))
        self.payload = self.Payload(payload_bytes)

    def encode(self):
        header = self.encode_header(self.header)
        payload = self.encode_payload(self.header.len, self.payload)

        return header + payload

    @staticmethod
    def encode_header(header):
        return pack(MessageGroup.HEADER_CODE, header.num_query, header.len)

    @staticmethod
    def encode_payload(len_payload, payload):
        return pack(f"!{len_payload}s", payload.data)

    @staticmethod
    def decode(msg):
        header = MessageGroup.decode_header(msg[: MessageGroup.SIZE_HEADER])
        payload = MessageGroup.decode_payload(msg[MessageGroup.SIZE_HEADER :])

        return header, payload

    @staticmethod
    def decode_header(header):
        return MessageGroup.Header._make(unpack(MessageGroup.HEADER_CODE, header))

    @staticmethod
    def decode_payload(payload_bytes):
        return MessageGroup._unpack_payload(payload_bytes)

    @staticmethod
    def _pack_payload(payload):
        payload_str = "\0".join(payload)
        return payload_str.encode("utf-8")

    @staticmethod
    def _unpack_payload(payload_bytes):
        payload = payload_bytes.decode("utf-8").split("\0")
        return MessageGroup.Payload(payload)
