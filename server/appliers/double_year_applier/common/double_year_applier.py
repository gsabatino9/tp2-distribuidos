from server.appliers.common.applier_controller import ApplierController


class DoubleYearApplier:
    def __init__(self, name_recv_queue, name_em_queue, name_send_queue, id_applier):
        operation = lambda k, v: (v[1] > 2 * v[0]) and (v[0] > 0)

        self.applier_controller = ApplierController(
            name_recv_queue,
            name_em_queue,
            name_send_queue,
            2,
            operation,
            self.gen_result_msg,
            id_applier
        )

    def gen_result_msg(self, trip, applier):
        key = trip[0]
        value = [int(i) for i in trip[1:]]

        result = applier.apply(key, value)

        return result, ",".join(trip)

    def stop(self):
        self.applier_controller.stop()
