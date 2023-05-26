from collections import namedtuple
from struct import pack, unpack, calcsize


class MessageClient:
    # Constants for data types
    STATION_DATA = 0
    WEATHER_DATA = 1
    TRIP_DATA = 2

    # Constants for message types
    SEND_DATA = 0
    SEND_LAST = 1

    # Constants for cities
    MONTREAL = 0
    TORONTO = 1
    WASHINGTON = 2

    # Struct format for message header
    HEADER_CODE = "!BBBI"
    # Size of header in bytes
    SIZE_HEADER = calcsize(HEADER_CODE)

    # Define the named tuples used in the protocol
    Header = namedtuple("Header", "data_type msg_type city len")
    Payload = namedtuple("Payload", "data")

    def __init__(self, data_type, msg_type, city, payload):
        if payload is None:
            payload = []
        payload_bytes = self._pack_payload(payload)

        self.header = self.Header(data_type, msg_type, city, len(payload_bytes))
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
            MessageClient.HEADER_CODE,
            header.data_type,
            header.msg_type,
            header.city,
            header.len,
        )

    @staticmethod
    def encode_payload(len_payload, payload):
        return pack(f"!{len_payload}s", payload.data)

    @staticmethod
    def decode(msg):
        header = MessageClient.decode_header(msg[: MessageClient.SIZE_HEADER])
        payload = MessageClient.decode_payload(msg[MessageClient.SIZE_HEADER :])

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
        return MessageClient.Header._make(unpack(MessageClient.HEADER_CODE, header))

    @staticmethod
    def decode_payload(payload_bytes):
        """
        Unpack the message payload from a string of null-separated strings.

        Args:
                payload_bytes (bytes): The packed payload.

        Returns:
                list[str]: A list of strings representing the message payload.
        """
        return MessageClient._unpack_payload(payload_bytes)

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
        return MessageClient.Payload(payload)

    @classmethod
    def station_message(cls, payload, city, is_last=False):
        data_type = cls.STATION_DATA
        msg_type = cls.SEND_LAST if is_last else cls.SEND_DATA

        return cls(data_type, msg_type, city, payload).encode()

    @classmethod
    def weather_message(cls, payload, city, is_last=False):
        data_type = cls.WEATHER_DATA
        msg_type = cls.SEND_LAST if is_last else cls.SEND_DATA
        return cls(data_type, msg_type, city, payload).encode()

    @classmethod
    def trip_message(cls, payload, city, is_last=False):
        data_type = cls.TRIP_DATA
        msg_type = cls.SEND_LAST if is_last else cls.SEND_DATA
        return cls(data_type, msg_type, city, payload).encode()
