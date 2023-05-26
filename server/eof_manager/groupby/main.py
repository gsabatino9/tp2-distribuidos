from common.eof_manager import EOFManager
import os, ast

NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_GROUPBY_QUEUE = os.environ.get("NAME_GROUPBY_QUEUE")
NAME_SEND_QUEUE = os.environ.get("NAME_SEND_QUEUE")


def main():
    name_groupby_queue = ast.literal_eval(NAME_GROUPBY_QUEUE)

    e = EOFManager(NAME_RECV_QUEUE, name_groupby_queue, NAME_SEND_QUEUE)
    e.stop()


if __name__ == "__main__":
    main()
