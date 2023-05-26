from server.filters.common.filter_controller import FilterController


class FilterDistance:
    def __init__(
        self, name_recv_exchange, name_recv_queue, name_em_queue, name_send_queue
    ):
        columns_names = """city,start_date,start_station_code,end_date,end_station_code,duration_sec,is_member,yearid,name_start_station,lat_start_station,long_start_station,name_end_station,lat_end_station,long_end_station"""
        reduced_columns = "city,lat_start_station,long_start_station,name_end_station,lat_end_station,long_end_station"
        func_filter = {"city": lambda x: x == "montreal"}

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
