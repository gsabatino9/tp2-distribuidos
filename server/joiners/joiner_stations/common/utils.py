from server.joiners.common.join_data import JoinData


class StationsData:
    def __init__(self, idx_code=0, idx_yearid=4, len_msg=5, storage=None):
        self._data = JoinData((idx_code, idx_yearid), len_msg, backing_storage=storage)

    def add_data(self, station):
        self._data.add_data(station)

    def join_trip(self, trip):
        start_code, end_code, yearid = trip[1], trip[3], trip[6]
        start_station = self._data.find_record((start_code, yearid))
        end_station = self._data.find_record((end_code, yearid))

        return ",".join(trip + start_station + end_station)
