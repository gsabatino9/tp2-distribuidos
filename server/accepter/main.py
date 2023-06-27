from common.accepter import Accepter
import os, ast

HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
NAME_STATIONS_QUEUE = os.environ.get("NAME_STATIONS_QUEUE")
NAME_WEATHER_QUEUE = os.environ.get("NAME_WEATHER_QUEUE")
NAME_TRIPS_QUEUES = os.environ.get("NAME_TRIPS_QUEUES")
NAME_EM_QUEUE = os.environ.get("NAME_EM_QUEUE")
NAME_STATUS_QUEUE = os.environ.get("NAME_STATUS_QUEUE")
NAME_SM_QUEUE = os.environ.get("NAME_SM_QUEUE")
NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
AMOUNT_QUERIES = int(os.environ.get("AMOUNT_QUERIES"))
SIZE_STATIONS = int(os.environ.get("SIZE_STATIONS"))
SIZE_WEATHER = int(os.environ.get("SIZE_WEATHER"))
SHARDING_AMOUNT = int(os.environ.get("SHARDING_AMOUNT"))


def main():
    name_trips_queues = ast.literal_eval(NAME_TRIPS_QUEUES)
    accepter = Accepter(
        HOST,
        PORT,
        NAME_STATIONS_QUEUE,
        NAME_WEATHER_QUEUE,
        name_trips_queues,
        NAME_EM_QUEUE,
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
