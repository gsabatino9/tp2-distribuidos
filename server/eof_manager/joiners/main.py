from common.eof_manager import EOFManager
import os

NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_SEND_QUEUE = os.environ.get("NAME_SEND_QUEUE")
NAME_STATIONS_QUEUE = os.environ.get("NAME_STATIONS_QUEUE")
NAME_WEATHER_QUEUE = os.environ.get("NAME_WEATHER_QUEUE")
NAME_JOIN_STATIONS_QUEUE = os.environ.get("NAME_JOIN_STATIONS_QUEUE")
NAME_JOIN_WEATHER_QUEUE = os.environ.get("NAME_JOIN_WEATHER_QUEUE")


def main():
    e = EOFManager(
        NAME_RECV_QUEUE,
        NAME_SEND_QUEUE,
        NAME_STATIONS_QUEUE,
        NAME_WEATHER_QUEUE,
        NAME_JOIN_STATIONS_QUEUE,
        NAME_JOIN_WEATHER_QUEUE,
    )
    e.stop()


if __name__ == "__main__":
    main()
