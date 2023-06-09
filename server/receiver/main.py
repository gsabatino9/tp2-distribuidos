from common.receiver import Receiver
import os, ast

HOST = os.environ.get("HOST")
PORT = int(os.environ.get("PORT"))
NAME_STATIONS_QUEUE = os.environ.get("NAME_STATIONS_QUEUE")
NAME_WEATHER_QUEUE = os.environ.get("NAME_WEATHER_QUEUE")
NAME_TRIPS_QUEUES = os.environ.get("NAME_TRIPS_QUEUES")
NAME_EM_QUEUE = os.environ.get("NAME_EM_QUEUE")
NAME_STATUS_QUEUE = os.environ.get("NAME_STATUS_QUEUE")
AMOUNT_QUERIES = int(os.environ.get("AMOUNT_QUERIES"))


def main():
    name_trips_queues = ast.literal_eval(NAME_TRIPS_QUEUES)
    receiver = Receiver(
        HOST,
        PORT,
        NAME_STATIONS_QUEUE,
        NAME_WEATHER_QUEUE,
        name_trips_queues,
        NAME_EM_QUEUE,
        NAME_STATUS_QUEUE,
        AMOUNT_QUERIES,
    )
    receiver.run()
    receiver.stop()


if __name__ == "__main__":
    main()
