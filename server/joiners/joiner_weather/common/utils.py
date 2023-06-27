from server.common.atomic_storage.atomic_storage import AtomicBucket
from server.joiners.common.join_data import JoinData


class WeatherData:
    def __init__(self, idx_date=0, len_msg=10, storage=None):
        self._data = JoinData((idx_date,), len_msg, backing_storage=storage)

    def add_data(self, weather):
        self._data.add_data(weather)

    def join_trip(self, trip):
        start_date, end_date = trip[0], trip[2]
        start_weather = self._data.find_record((start_date,))
        end_weather = self._data.find_record((end_date,))

        return ",".join(trip + start_weather + end_weather)

    def drop(self):
        self._data.drop()
