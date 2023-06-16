from protocol.communication import Communication
from protocol.message_client import MessageClient
from protocol.message_server import MessageServer
from protocol.utils import suscriptions_to_number


class CommunicationClient:
    """
    Represents a communication client for sending and receiving messages to/from the server.
    """

    def __init__(self, socket, suscriptions):
        """
        Initializes a new CommunicationClient object.

        Parameters:
        socket (socket): The socket object used for communication.
        """
        self.comm = Communication(socket)
        self.queries_suscriptions = suscriptions_to_number(suscriptions)

    def getpeername(self):
        return self.comm.getpeername()

    def set_id_client(self, id_client):
        self.msg = MessageClient(id_client, self.queries_suscriptions)

    def send(self, data_type, data, is_last=False):
        if data_type == "stations":
            self.__send_stations(data, is_last)
        elif data_type == "weather":
            self.__send_weathers(data, is_last)
        else:
            self.__send_trips(data, is_last)

    def send_get_results(self):
        msg = self.msg.get_results_messages()
        self.comm.send_message(msg)

    def __send_stations(self, stations, is_last=False):
        msg = self.msg.station_message(stations, is_last)
        self.comm.send_message(msg)

    def __send_weathers(self, weathers, is_last=False):
        msg = self.msg.weather_message(weathers, is_last)
        self.comm.send_message(msg)

    def __send_trips(self, trips, is_last=False):
        msg = self.msg.trip_message(trips, is_last)
        self.comm.send_message(msg)

    def recv_id_client(self):
        header, _ = self.__recv_message()
        self.msg = MessageClient(header.id_query, self.queries_suscriptions)

        return header.id_query

    def recv_ack(self):
        return self.__recv_message()

    def recv_results(self):
        return self.__recv_message(decode_payload=True)

    def __recv_message(self, decode_payload=False):
        header = self.__recv_header()
        payload = self.__recv_payload(header.len, decode_payload=decode_payload)

        return header, payload

    def __recv_header(self):
        header = self.comm.recv_header(MessageServer.SIZE_HEADER)
        header = MessageServer.decode_header(header)

        return header

    def __recv_payload(self, len_payload, decode_payload=True):
        payload = self.comm.recv_payload(len_payload)
        if decode_payload:
            payload = MessageServer.decode_payload(payload)

        return payload

    def stop(self):
        """
        Closes the connection with the server.
        """
        self.comm.stop()
