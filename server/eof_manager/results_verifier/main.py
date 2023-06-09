from common.eof_manager import EOFManager
import os

NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_VERIFIER_QUEUE = os.environ.get("NAME_VERIFIER_QUEUE")
NAME_STATUS_QUEUE = os.environ.get("NAME_STATUS_QUEUE")
SIZE_QUERIES = int(os.environ.get("SIZE_QUERIES"))


def main():
    e = EOFManager(
        NAME_RECV_QUEUE, NAME_VERIFIER_QUEUE, NAME_STATUS_QUEUE, SIZE_QUERIES
    )
    e.stop()


if __name__ == "__main__":
    main()
