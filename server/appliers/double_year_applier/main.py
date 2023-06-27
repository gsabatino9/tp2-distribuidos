from common.double_year_applier import DoubleYearApplier
import os

NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_EM_QUEUE = os.environ.get("NAME_EM_QUEUE")
NAME_SEND_QUEUE = os.environ.get("NAME_SEND_QUEUE")
ID_APPLIER = os.environ.get("ID_APPLIER")


def main():
    a = DoubleYearApplier(NAME_RECV_QUEUE+ID_APPLIER, NAME_EM_QUEUE, NAME_SEND_QUEUE)
    a.stop()


if __name__ == "__main__":
    main()
