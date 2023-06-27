from common.groupby_start_station import GroupbyStartStation
import os

NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_EM_QUEUE = os.environ.get("NAME_EM_QUEUE")
NAME_SEND_QUEUE = os.environ.get("NAME_SEND_QUEUE")
SIZE_WORKERS_SEND = int(os.environ.get("SIZE_WORKERS_SEND"))
CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE"))


def main():
    g = GroupbyStartStation(NAME_RECV_QUEUE, NAME_EM_QUEUE, NAME_SEND_QUEUE, SIZE_WORKERS_SEND, CHUNK_SIZE)
    g.stop()


if __name__ == "__main__":
    main()
