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


def is_trip(header):
    return header.data_type == MessageClient.TRIP_DATA


def results_message(id_query, id_batch, batch_results):
    return MessageServer.results_message(id_query, id_batch, batch_results)


def is_eof(body):
    try:
        decode(body)
        return False
    except:
        return True


def construct_msg(header, trips_array):
    return MessageClient(
        header.data_type,
        header.msg_type,
        header.id_client,
        header.id_batch,
        header.queries_suscriptions,
        trips_array,
    ).encode()


def customer_subscribed_to_query(header, id_query):
    list_suscriptions = number_to_suscriptions(header.queries_suscriptions)
    return id_query in list_suscriptions


def last_message():
    return MessageServer.last_chunk_message()


def is_last_message(body):
    header, _ = MessageServer.decode(body)
    return header.msg_type == MessageServer.SEND_LAST_RESULT
