from common.eof_manager import EOFManager
import os

NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_SEND_QUEUE = os.environ.get("NAME_SEND_QUEUE")
NAME_STATIONS_QUEUE = os.environ.get("NAME_STATIONS_QUEUE")
NAME_WEATHER_QUEUE = os.environ.get("NAME_WEATHER_QUEUE")
NAME_STATUS_QUEUE = os.environ.get("NAME_STATUS_QUEUE")
SIZE_STATIONS = int(os.environ.get("SIZE_STATIONS"))
SIZE_WEATHER = int(os.environ.get("SIZE_WEATHER"))


def main():
    e = EOFManager(
        NAME_RECV_QUEUE,
        NAME_SEND_QUEUE,
        NAME_STATIONS_QUEUE,
        NAME_WEATHER_QUEUE,
        NAME_STATUS_QUEUE,
        SIZE_STATIONS,
        SIZE_WEATHER,
    )
    e.stop()


if __name__ == "__main__":
    main()
