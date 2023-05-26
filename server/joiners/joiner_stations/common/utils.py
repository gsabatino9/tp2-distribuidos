class StationsData:
    def __init__(self, idx_code=0, idx_yearid=4, len_msg=5):
        self.stations = {}
        self.idx_code = idx_code
        self.idx_yearid = idx_yearid
        self.idxs_joined_data = []

        for i in range(len_msg):
            if i != idx_code and i != idx_yearid:
                self.idxs_joined_data.append(i)

    def add_data(self, city, station):
        code, yearid = station[self.idx_code], station[self.idx_yearid]
        self.stations[city, code, yearid] = [
            elem for i, elem in enumerate(station) if i in self.idxs_joined_data
        ]

    def join_trip(self, city, trip):
        try:
            start_code, end_code, yearid = trip[1], trip[3], trip[6]
            start_station = self.__join_trip(city, start_code, yearid)
            end_station = self.__join_trip(city, end_code, yearid)

            return ",".join([city] + trip + start_station + end_station)
        except:
            return None

    def __join_trip(self, city, code, yearid):
        return self.stations[city, code, yearid]
