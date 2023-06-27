from common.joiner_stations import JoinerStations
import os, ast

NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_TRIPS_QUEUE = os.environ.get("NAME_TRIPS_QUEUE")
NAME_EM_QUEUE = os.environ.get("NAME_EM_QUEUE")
NAME_NEXT_STAGE_QUEUE = os.environ.get("NAME_NEXT_STAGE_QUEUE")
SIZE_WORKERS = os.environ.get("SIZE_WORKERS")
ID_JOINER = os.environ.get("ID_JOINER")


def main():
    name_filters_queue = ast.literal_eval(NAME_NEXT_STAGE_QUEUE)
    size_workers = ast.literal_eval(SIZE_WORKERS)
    j = JoinerStations(
        NAME_RECV_QUEUE+ID_JOINER,
        NAME_TRIPS_QUEUE,
        NAME_EM_QUEUE,
        name_filters_queue,
        size_workers,
    )
    j.stop()


if __name__ == "__main__":
    main()
