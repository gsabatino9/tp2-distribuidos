from common.utils import WeatherData
from server.joiners.common.joiner_controller import JoinerController
from server.joiners.common.joiner_state import JoinerState


class JoinerWeather:
    def __init__(
        self, name_recv_queue, name_trips_queue, name_em_queue, name_next_stage_queue
    ):
        self.joiner = JoinerController(
            name_recv_queue,
            name_trips_queue,
            name_em_queue,
            name_next_stage_queue,
            JoinerState(lambda bucket: WeatherData(storage=bucket)),
        )

    def stop(self):
        self.joiner.stop()
