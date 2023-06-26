from server.appliers.common.applier_controller import ApplierController


class MeanDistanceApplier:
    def __init__(self, name_recv_queue, name_em_queue, name_send_queue, id_applier):
        operation = lambda k, v: (v[0] / v[1] >= 6) if v[1] > 0 and v[0] > 0 else False

        self.applier_controller = ApplierController(
            name_recv_queue,
            name_em_queue,
            name_send_queue,
            3,
            operation,
            self.gen_result_msg,
            id_applier,
        )

    def gen_result_msg(self, trip, applier):
        key = trip[0]
        value = [float(i) for i in trip[1:]]

        result = applier.apply(key, value)
        if result:
            ret = f"{key},{value[0] / value[1]}"
        else:
            ret = f"{key}"

        return result, ret

    def stop(self):
        self.applier_controller.stop()
