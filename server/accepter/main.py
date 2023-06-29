from common.accepter import Accepter
import os, ast

HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
NAME_STATIONS_QUEUE = os.environ.get("NAME_STATIONS_QUEUE")
NAME_WEATHER_QUEUE = os.environ.get("NAME_WEATHER_QUEUE")
NODES_TO_SEND_TRIPS = os.environ.get("NODES_TO_SEND_TRIPS")
NAME_STATUS_QUEUE = os.environ.get("NAME_STATUS_QUEUE")
NAME_SM_QUEUE = os.environ.get("NAME_SM_QUEUE")
NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
AMOUNT_QUERIES = int(os.environ.get("AMOUNT_QUERIES"))
SIZE_STATIONS = int(os.environ.get("SIZE_STATIONS"))
SIZE_WEATHER = int(os.environ.get("SIZE_WEATHER"))
SHARDING_AMOUNT = int(os.environ.get("SHARDING_AMOUNT"))


def main():
    nodes_to_send_trips = ast.literal_eval(NODES_TO_SEND_TRIPS)
    accepter = Accepter(
        HOST,
        PORT,
        NAME_STATIONS_QUEUE,
        NAME_WEATHER_QUEUE,
        nodes_to_send_trips,
        NAME_STATUS_QUEUE,
        NAME_SM_QUEUE,
        NAME_RECV_QUEUE,
        AMOUNT_QUERIES,
        SIZE_STATIONS,
        SIZE_WEATHER,
        SHARDING_AMOUNT,
    )
    accepter.run()
    accepter.stop()


if __name__ == "__main__":
    main()
