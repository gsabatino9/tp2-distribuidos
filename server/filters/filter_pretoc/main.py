from common.filter_pretoc import FilterPretoc
import os, ast

ID_QUERY = int(os.environ.get("ID_QUERY"))
NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_EM_QUEUE = os.environ.get("NAME_EM_QUEUE")
NODE_TO_SEND_TRIPS = os.environ.get("NODE_TO_SEND_TRIPS")
ID_FILTER = os.environ.get("ID_FILTER")


def main():
    f = FilterPretoc(
        ID_QUERY,
        NAME_RECV_QUEUE + ID_FILTER,
        NAME_EM_QUEUE,
        ast.literal_eval(str(NODE_TO_SEND_TRIPS)),
    )
    f.stop()


if __name__ == "__main__":
    main()
