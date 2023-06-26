from common.filter_year import FilterYear
import os

ID_QUERY = int(os.environ.get("ID_QUERY"))
NAME_RECV_EXCHANGE = os.environ.get("NAME_RECV_EXCHANGE")
NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_EM_QUEUE = os.environ.get("NAME_EM_QUEUE")
NAME_SEND_QUEUE = os.environ.get("NAME_SEND_QUEUE")
ID_FILTER = int(os.environ.get("ID_FILTER"))


def main():
    f = FilterYear(
        ID_QUERY, NAME_RECV_EXCHANGE, NAME_RECV_QUEUE, NAME_EM_QUEUE, NAME_SEND_QUEUE, ID_FILTER
    )
    f.stop()


if __name__ == "__main__":
    main()
