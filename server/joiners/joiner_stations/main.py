from common.joiner_stations import JoinerStations
import os

NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_TRIPS_QUEUE = os.environ.get("NAME_TRIPS_QUEUE")
NAME_EM_QUEUE = os.environ.get("NAME_EM_QUEUE")
NAME_NEXT_STAGE_QUEUE = os.environ.get("NAME_NEXT_STAGE_QUEUE")


def main():
    j = JoinerStations(
        NAME_RECV_QUEUE, NAME_TRIPS_QUEUE, NAME_EM_QUEUE, NAME_NEXT_STAGE_QUEUE
    )
    j.stop()


if __name__ == "__main__":
    main()
