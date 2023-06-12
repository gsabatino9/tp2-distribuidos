from common.filter_pretoc import FilterPretoc
import os

ID_QUERY = int(os.environ.get("ID_QUERY"))
NAME_RECV_EXCHANGE = os.environ.get("NAME_RECV_EXCHANGE")
NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_EM_QUEUE = os.environ.get("NAME_EM_QUEUE")
NAME_SEND_QUEUE = os.environ.get("NAME_SEND_QUEUE")


def main():
    f = FilterPretoc(
        ID_QUERY, NAME_RECV_EXCHANGE, NAME_RECV_QUEUE, NAME_EM_QUEUE, NAME_SEND_QUEUE
    )
    f.stop()


if __name__ == "__main__":
    main()
