from common.eof_manager import EOFManager
import os, ast

NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_APPLIERS_QUEUES = os.environ.get("NAME_APPLIERS_QUEUES")
NAME_SEND_QUEUE = os.environ.get("NAME_SEND_QUEUE")
SIZE_WORKERS = os.environ.get("SIZE_WORKERS")


def main():
    name_appliers_queues = ast.literal_eval(NAME_APPLIERS_QUEUES)
    size_workers = ast.literal_eval(SIZE_WORKERS)

    e = EOFManager(NAME_RECV_QUEUE, name_appliers_queues, NAME_SEND_QUEUE, size_workers)
    e.stop()


if __name__ == "__main__":
    main()
