class WeatherData:
    def __init__(self, idx_date=0, len_msg=10):
        self.weathers = {}
        self.idx_date = idx_date
        self.idxs_joined_data = []

        for i in range(len_msg):
            if i != idx_date:
                self.idxs_joined_data.append(i)

    def add_data(self, id_client, weather):
        idx_date = weather[self.idx_date]
        self.weathers[id_client, idx_date] = [
            elem for i, elem in enumerate(weather) if i in self.idxs_joined_data
        ]

    def join_trip(self, id_client, trip):
        try:
            start_date, end_date = trip[0], trip[2]
            start_weather = self.__join_trip(id_client, start_date)
            end_weather = self.__join_trip(id_client, end_date)

            return ",".join(trip + start_weather + end_weather)
        except:
            return None

    def __join_trip(self, id_client, date):
        return self.weathers[id_client, date]

    def delete_client(self, id_client):
        keys_to_delete = [key for key in self.weathers.keys() if key[0] == id_client]
        for key in keys_to_delete:
            del self.weathers[key]
