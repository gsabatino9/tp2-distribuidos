class WeatherData:
    def __init__(self, idx_date=0, len_msg=10):
        self.weathers = {}
        self.idx_date = idx_date
        self.idxs_joined_data = []

        for i in range(len_msg):
            if i != idx_date:
                self.idxs_joined_data.append(i)

    def add_data(self, city, weather):
        idx_date = weather[self.idx_date]
        self.weathers[city, idx_date] = [
            elem for i, elem in enumerate(weather) if i in self.idxs_joined_data
        ]

    def join_trip(self, city, trip):
        try:
            start_date, end_date = trip[0], trip[2]
            start_weather = self.__join_trip(city, start_date)
            end_weather = self.__join_trip(city, end_date)

            return ",".join([city] + trip + start_weather + end_weather)
        except:
            return None

    def __join_trip(self, city, date):
        return self.weathers[city, date]
