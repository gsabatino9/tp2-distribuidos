from protocol.message_client import MessageClient
from protocol.message_server import MessageServer
from protocol.utils import number_to_suscriptions


def decode(body):
    header, trips_array = MessageClient.decode(body)
    return header, trips_array[0]


def encode_header(header):
    return MessageClient.encode_header(header)


def is_station(header):
    return header.data_type == MessageClient.STATION_DATA


def is_weather(header):
    return header.data_type == MessageClient.WEATHER_DATA


def results_message(self, id_batch, batch_results):
    return MessageServer.results_message(1, id_batch, batch_results)


def is_eof(body):
    try:
        decode(body)
        return False
    except:
        return True


def get_id_client(self, body):
    header, _ = decode(body)
    return header.id_client


def construct_msg(header, trips_array):
    msg_client = MessageClient(header.id_client, header.queries_suscriptions)

    return msg_client.new_message(header.data_type, header.msg_type, trips_array)


def customer_subscribed_to_query(header, id_query):
    list_suscriptions = number_to_suscriptions(header.queries_suscriptions)
    return id_query in list_suscriptions


def last_message(self):
    return MessageServer.last_chunk_message(id_batch)