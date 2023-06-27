from server.groupby.common.groupby_controller import GroupbyController


class GroupbyAllElements:
    def __init__(
        self,
        name_recv_queue,
        name_em_queue,
        name_send_queue,
        size_workers_send,
        chunk_size,
    ):
        def operation(old, new):
            if new > 0:
                return [old[0] + new, old[1] + 1]
            else:
                return old

        base_data = [0, 0]

        self.groupby_controller = GroupbyController(
            name_recv_queue,
            name_em_queue,
            name_send_queue,
            size_workers_send,
            operation,
            base_data,
            self.gen_key_value,
            chunk_size,
        )

    def gen_key_value(self, trip):
        # trip[4] := duration_sec
        return "mean_duration_trips", float(trip[4])

    def stop(self):
        self.groupby_controller.stop()
