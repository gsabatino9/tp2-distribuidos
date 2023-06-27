from common.utils import WeatherData
from server.joiners.common.joiner_controller import JoinerController
from server.joiners.common.joiner_state import JoinerState
from server.common.utils_messages_client import is_weather


class JoinerWeather:
    def __init__(
        self,
        name_recv_queue,
        name_trips_queue,
        name_em_queue,
        name_next_stage_queues,
        size_workers_next_stage,
    ):
        self.joiner = JoinerController(
            name_recv_queue,
            name_trips_queue,
            name_em_queue,
            name_next_stage_queues,
            size_workers_next_stage,
            JoinerState(lambda bucket: WeatherData(storage=bucket)),
            lambda data: is_weather(data),
        )

    def stop(self):
        self.joiner.stop()
