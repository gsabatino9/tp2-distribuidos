from collections import namedtuple
from struct import pack, unpack, calcsize


class MessageServer:
    # Constants for message types
    FILES_RECEIVED = 0
    QUERIES_PROCESSED = 1
    SEND_LAST = 2

    # Struct format for message header
    HEADER_CODE = "!BBI"
    # Size of header in bytes
    SIZE_HEADER = calcsize(HEADER_CODE)

    # Define the named tuples used in the protocol
    Header = namedtuple("Header", "msg_type id_query len")
    Payload = namedtuple("Payload", "data")

    def __init__(self, msg_type, id_query, payload):
        if payload is None:
            payload = list("")
        payload_bytes = self._pack_payload(payload)

        self.header = self.Header(msg_type, id_query, len(payload_bytes))
        self.payload = self.Payload(payload_bytes)

    def encode(self):
        """
        Encode the message as bytes to be sent over the network.

        Returns:
                bytes: The encoded message as bytes.
        """
        header = self.encode_header(self.header)
        payload = self.encode_payload(self.header.len, self.payload)

        return header + payload

    @staticmethod
    def encode_header(header):
        return pack(
            MessageServer.HEADER_CODE, header.msg_type, header.id_query, header.len
        )

    @staticmethod
    def encode_payload(len_payload, payload):
        return pack(f"!{len_payload}s", payload.data)

    @staticmethod
    def decode(msg):
        header = MessageServer.decode_header(msg[: MessageServer.SIZE_HEADER])
        payload = MessageServer.decode_payload(msg[MessageServer.SIZE_HEADER :])

        return header, payload

    @staticmethod
    def decode_header(header):
        """
        Decode the message header from bytes.

        Args:
                header (bytes): The message header as bytes.

        Returns:
                Header: A named tuple representing the message header.
        """
        return MessageServer.Header._make(unpack(MessageServer.HEADER_CODE, header))

    @staticmethod
    def decode_payload(payload_bytes):
        """
        Unpack the message payload from a string of null-separated strings.

        Args:
                payload_bytes (bytes): The packed payload.

        Returns:
                list[str]: A list of strings representing the message payload.
        """
        return MessageServer._unpack_payload(payload_bytes)

    @staticmethod
    def _pack_payload(payload):
        """
        Pack the message payload as a string of null-separated strings.

        Args:
                payload (list[str]): A list of strings to be packed.

        Returns:
                bytes: The packed payload as bytes.
        """
        payload_str = "\0".join(payload)
        return payload_str.encode("utf-8")

    @staticmethod
    def _unpack_payload(payload_bytes):
        """
        Unpack the message payload from a string of null-separated strings.

        Args:
                payload_bytes (bytes): The packed payload.

        Returns:
                list[str]: A list of strings representing the message payload.
        """
        payload = payload_bytes.decode("utf-8").split("\0")
        return MessageServer.Payload(payload)

    @classmethod
    def files_received_message(cls):
        return cls(cls.FILES_RECEIVED, 0, list("")).encode()

    @classmethod
    def results_message(cls, id_query, results):
        return cls(cls.QUERIES_PROCESSED, id_query, results).encode()

    @classmethod
    def last_chunk_message(cls):
        return cls(cls.SEND_LAST, 0, list("")).encode()
