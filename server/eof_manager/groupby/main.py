from common.eof_manager import EOFManager
import os, ast

NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NODES_GROUPBY = os.environ.get("NODES_GROUPBY")
NAME_SEND_QUEUE = os.environ.get("NAME_SEND_QUEUE")
NAME_STATUS_QUEUE = os.environ.get("NAME_STATUS_QUEUE")


def main():
    nodes_groupby = ast.literal_eval(NODES_GROUPBY)

    e = EOFManager(NAME_RECV_QUEUE, nodes_groupby, NAME_SEND_QUEUE, NAME_STATUS_QUEUE)
    e.stop()


if __name__ == "__main__":
    main()
