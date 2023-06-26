from common.eof_manager import EOFManager
import os, ast

NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_FILTERS_EXCHANGE = os.environ.get("NAME_FILTERS_EXCHANGE")
NAME_FILTERS_QUEUE = os.environ.get("NAME_FILTERS_QUEUE")
NAME_SEND_QUEUE = os.environ.get("NAME_SEND_QUEUE")
NAME_STATUS_QUEUE = os.environ.get("NAME_STATUS_QUEUE")
SIZE_WORKERS = os.environ.get("SIZE_WORKERS")


def main():
    name_filters_queue = ast.literal_eval(NAME_FILTERS_QUEUE)
    size_workers = ast.literal_eval(SIZE_WORKERS)
    e = EOFManager(
        NAME_RECV_QUEUE,
        NAME_FILTERS_EXCHANGE,
        name_filters_queue,
        NAME_SEND_QUEUE,
        NAME_STATUS_QUEUE,
        size_workers,
    )
    e.stop()


if __name__ == "__main__":
    main()
