class StationsData:
    def __init__(self, idx_code=0, idx_yearid=4, len_msg=5):
        self.stations = {}
        self.idx_code = idx_code
        self.idx_yearid = idx_yearid
        self.idxs_joined_data = []

        for i in range(len_msg):
            if i != idx_code and i != idx_yearid:
                self.idxs_joined_data.append(i)

    def add_data(self, id_client, station):
        code, yearid = station[self.idx_code], station[self.idx_yearid]
        self.stations[id_client, code, yearid] = [
            elem for i, elem in enumerate(station) if i in self.idxs_joined_data
        ]

    def join_trip(self, id_client, trip):
        try:
            start_code, end_code, yearid = trip[1], trip[3], trip[6]
            start_station = self.__join_trip(id_client, start_code, yearid)
            end_station = self.__join_trip(id_client, end_code, yearid)

            return ",".join(trip + start_station + end_station)
        except:
            return None

    def __join_trip(self, id_client, code, yearid):
        return self.stations[id_client, code, yearid]

    def delete_client(self, id_client):
        keys_to_delete = [key for key in self.stations.keys() if key[0] == id_client]
        for key in keys_to_delete:
            del self.stations[key]
