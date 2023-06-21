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
    GET_ID = 2
    GET_RESULTS = 3

    # Struct format for message header
    DATA_TYPE_LEN = "B"
    MSG_TYPE_LEN = "B"
    ID_CLIENT_LEN = "Q"
    ID_BATCH_LEN = "I"
    QUERIES_SUSCRIPTIONS_LEN = "B"
    LEN_PAYLOAD_LEN = "I"
    HEADER_CODE = (
        "!"
        + DATA_TYPE_LEN
        + MSG_TYPE_LEN
        + ID_CLIENT_LEN
        + ID_BATCH_LEN
        + QUERIES_SUSCRIPTIONS_LEN
        + LEN_PAYLOAD_LEN
    )
    # Size of header in bytes
    SIZE_HEADER = calcsize(HEADER_CODE)

    # Define the named tuples used in the protocol
    Header = namedtuple(
        "Header", "data_type msg_type id_client id_batch queries_suscriptions len"
    )
    Payload = namedtuple("Payload", "data")

    def __init__(self, id_client, queries_suscriptions):
        self.id_client = id_client
        self.queries_suscriptions = queries_suscriptions
        self.id_batch = 0

    def new_message(self, data_type, msg_type, payload):
        if payload is None:
            payload = []
        payload_bytes = self._pack_payload(payload)

        header = self.Header(
            data_type,
            msg_type,
            self.id_client,
            self.id_batch,
            self.queries_suscriptions,
            len(payload_bytes),
        )
        self.id_batch += 1
        payload = self.Payload(payload_bytes)

        return self.encode(header, payload)

    """
    def __init__(self, data_type, msg_type, queries_suscriptions, payload):
        if payload is None:
            payload = []
        payload_bytes = self._pack_payload(payload)

        self.header = self.Header(
            data_type, msg_type, queries_suscriptions, len(payload_bytes)
        )
        self.payload = self.Payload(payload_bytes)
    """

    def encode(self, header, payload):
        """
        Encode the message as bytes to be sent over the network.

        Returns:
                bytes: The encoded message as bytes.
        """
        encoded_header = self.encode_header(header)
        encoded_payload = self.encode_payload(header.len, payload)

        return encoded_header + encoded_payload

    @staticmethod
    def encode_header(header):
        return pack(MessageClient.HEADER_CODE, *header)

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

    def station_message(self, payload, is_last=False):
        data_type = self.STATION_DATA
        msg_type = self.SEND_LAST if is_last else self.SEND_DATA

        return self.new_message(data_type, msg_type, payload)

    def weather_message(self, payload, is_last=False):
        data_type = self.WEATHER_DATA
        msg_type = self.SEND_LAST if is_last else self.SEND_DATA
        return self.new_message(data_type, msg_type, payload)

    def trip_message(self, payload, is_last=False):
        data_type = self.TRIP_DATA
        msg_type = self.SEND_LAST if is_last else self.SEND_DATA
        return self.new_message(data_type, msg_type, payload)

    def get_id_message(self):
        msg_type = self.GET_ID
        return self.new_message(self.TRIP_DATA, msg_type, list(""))

    def get_results_message(self):
        msg_type = self.GET_RESULTS
        return self.new_message(self.TRIP_DATA, msg_type, list(""))
