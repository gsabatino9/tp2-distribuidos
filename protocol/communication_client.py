from protocol.communication import Communication
from protocol.message_client import MessageClient
from protocol.message_server import MessageServer


class CommunicationClient:
    """
    Represents a communication client for sending and receiving messages to/from the server.
    """

    def __init__(self, socket):
        """
        Initializes a new CommunicationClient object.

        Parameters:
        socket (socket): The socket object used for communication.
        """
        self.comm = Communication(socket)

    def getpeername(self):
        return self.comm.getpeername()

    def send(self, data_type, data, city, is_last=False):
        if data_type == "stations":
            self.__send_stations(data, city, is_last)
        elif data_type == "weather":
            self.__send_weathers(data, city, is_last)
        else:
            self.__send_trips(data, city, is_last)

    def __send_stations(self, stations, city, is_last=False):
        msg = MessageClient.station_message(stations, city, is_last)
        self.comm.send_message(msg)

    def __send_weathers(self, weathers, city, is_last=False):
        msg = MessageClient.weather_message(weathers, city, is_last)
        self.comm.send_message(msg)

    def __send_trips(self, trips, city, is_last=False):
        msg = MessageClient.trip_message(trips, city, is_last)
        self.comm.send_message(msg)

    def recv_files_received(self):
        header = self.__recv_header()
        payload = self.__recv_payload(header.len, decode_payload=False)

        return header, payload

    def recv_results(self):
        header = self.__recv_header()
        payload = self.__recv_payload(header.len, decode_payload=True)

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
