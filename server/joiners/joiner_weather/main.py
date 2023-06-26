from common.joiner_weather import JoinerWeather
import os, ast

NAME_RECV_QUEUE = os.environ.get("NAME_RECV_QUEUE")
NAME_TRIPS_QUEUE = os.environ.get("NAME_TRIPS_QUEUE")
NAME_EM_QUEUE = os.environ.get("NAME_EM_QUEUE")
NAME_NEXT_STAGE_EXCHANGE = os.environ.get("NAME_NEXT_STAGE_EXCHANGE")
NAME_NEXT_STAGE_QUEUE = os.environ.get("NAME_NEXT_STAGE_QUEUE")
SIZE_WORKERS = os.environ.get("SIZE_WORKERS")


def main():
    name_filters_queue = ast.literal_eval(NAME_NEXT_STAGE_QUEUE)
    size_workers = ast.literal_eval(SIZE_WORKERS)
    j = JoinerWeather(
        NAME_RECV_QUEUE,
        NAME_TRIPS_QUEUE,
        NAME_EM_QUEUE,
        NAME_NEXT_STAGE_EXCHANGE,
        name_filters_queue,
        size_workers,
    )
    j.stop()


if __name__ == "__main__":
    main()
