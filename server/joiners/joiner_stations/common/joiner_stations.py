from common.utils import StationsData
from server.joiners.common.joiner_controller import JoinerController


class JoinerStations:
    def __init__(
        self, name_recv_queue, name_trips_queue, name_em_queue, name_next_stage_queue
    ):
        self.joiner = JoinerController(
            name_recv_queue,
            name_trips_queue,
            name_em_queue,
            name_next_stage_queue,
            StationsData(),
        )

    def stop(self):
        self.joiner.stop()
