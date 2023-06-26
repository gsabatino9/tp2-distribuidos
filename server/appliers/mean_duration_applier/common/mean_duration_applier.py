from server.appliers.common.applier_controller import ApplierController


class MeanDurationApplier:
    def __init__(
        self, name_recv_queue, name_em_queue, name_send_queue, id_query, id_applier
    ):
        operation = lambda k, v: [k, str(v[0] / v[1])]
        self.applier_controller = ApplierController(
            name_recv_queue,
            name_em_queue,
            name_send_queue,
            id_query,
            operation,
            self.gen_result_msg,
            id_applier,
        )

    def gen_result_msg(self, trip, applier):
        key = trip[0]
        value = [float(i) for i in trip[1:]]

        result = applier.apply(key, value)
        msg_to_send = ",".join(result)

        return result, msg_to_send

    def stop(self):
        self.applier_controller.stop()
