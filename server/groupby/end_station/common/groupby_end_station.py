from server.groupby.common.groupby_controller import GroupbyController
from haversine import haversine


class GroupbyEndStation:
    def __init__(self, name_recv_queue, name_em_queue, name_send_queue, chunk_size):
        operation = lambda old, new: [old[0] + max(new, 0), old[1] + 1]
        base_data = [0, 0]

        self.groupby_controller = GroupbyController(
            name_recv_queue,
            name_em_queue,
            name_send_queue,
            operation,
            base_data,
            self.gen_key_value,
            chunk_size,
        )

    def gen_key_value(self, trip):
        distance = haversine(
            (float(trip[1]), float(trip[2])), (float(trip[4]), float(trip[5]))
        )

        return trip[3], distance

    def stop(self):
        self.groupby_controller.stop()
