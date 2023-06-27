from common.utils import StationsData
from server.joiners.common.joiner_controller import JoinerController
from server.joiners.common.joiner_state import JoinerState
from server.common.utils_messages_client import is_station


class JoinerStations:
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
            JoinerState(lambda _: StationsData()),
            lambda data: is_station(data),
        )

    def stop(self):
        self.joiner.stop()
