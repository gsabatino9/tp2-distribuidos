from server.filters.common.filter_controller import FilterController


class FilterPretoc:
    def __init__(
        self, name_recv_exchange, name_recv_queue, name_em_queue, name_send_queue
    ):
        columns_names = """city,start_date,start_station_code,end_date,end_station_code,duration_sec,is_member,yearid,start_prectot,start_qv2m,start_rh2m,start_ps,start_t2m_range,start_ts,start_t2mdew,start_t2mwet,start_t2m_max,end_prectot,end_qv2m,end_rh2m,end_ps,end_t2m_range,end_ts,end_t2mdew,end_t2mwet,end_t2m_max"""
        reduced_columns = "start_date,duration_sec,start_prectot"
        func_filter = {"start_prectot": lambda x: float(x) > 30.0}

        self.filter_controller = FilterController(
            name_recv_exchange,
            name_recv_queue,
            name_em_queue,
            name_send_queue,
            columns_names,
            reduced_columns,
            func_filter,
        )

    def stop(self):
        self.filter_controller.stop()
