import pandas as pd
from datetime import datetime, timedelta
import requests, zipfile, io
import os.path
from os import path

pd.set_option('display.max_columns', None)


class GTFS:
    URL = "https://ckan.multimediagdansk.pl/dataset/c24aa637-3619-4dc2-a171-a23eec8f2172/resource/30e783e4-2bec-4a7d-bb22-ee3e3b26ca96/download/gtfsgoogle.zip"
    result = pd.DataFrame()

    def download_data(self):
        if not (path.exists("data/stops.txt") &
                path.exists("data/routes.txt") &
                path.exists("data/stop_times.txt") &
                path.exists("data/trips.txt") &
                path.exists("data/shapes.txt") &
                path.exists("data/calendar_dates.txt")):
            print("Downloading data")
            r = requests.get(self.URL)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall("data")
            print("Download completed")

    def prepare_data(self):
        """
        Prepare needed data and saves it to csv located at data/processed_data.csv
        """
        self.download_data()

        print("Load csvs")
        df_stops = pd.read_csv('data/stops.txt')
        df_routes = pd.read_csv('data/routes.txt')
        df_stoptimes = pd.read_csv('data/stop_times.txt')
        df_trips = pd.read_csv('data/trips.txt')
        df_shapes = pd.read_csv('data/shapes.txt')
        df_dates = pd.read_csv('data/calendar_dates.txt')
        print("Loading completed")

        columns_to_drop = ['stop_headsign', 'stop_code', 'route_long_name', 'route_desc', 'route_color',
                           'route_text_color',
                           'trip_short_name']

        print("Merging columns")
        result = pd.merge(df_stoptimes, df_stops, how='inner', on='stop_id')
        result = pd.merge(result, df_trips, how='inner', on='trip_id')
        result = pd.merge(result, df_routes, how='inner', on='route_id')
        result = pd.merge(result, df_dates, how='inner', on='service_id')
        print("Merging completed")

        result = result.drop(columns=columns_to_drop)

        print("Process times")
        result['arrival_time_minutes'] = result['arrival_time'].map(lambda x: int(x[3:5]))
        result['arrival_time_hours'] = result['arrival_time'].map(lambda x: int(x[:2]))
        result['departure_time_minutes'] = result['departure_time'].map(lambda x: int(x[3:5]))
        result['departure_time_hours'] = result['departure_time'].map(lambda x: int(x[:2]))

        result['arrival_time_hours'] = result['arrival_time_hours'].apply(lambda x: x - 24 if x >= 24 else x)
        result['departure_time_hours'] = result['departure_time_hours'].apply(lambda x: x - 24 if x >= 24 else x)

        result.date = result.date.astype('str')
        result['month'] = result['date'].map(lambda x: x[4:6])
        result['day'] = result['date'].map(lambda x: x[6:8])
        result['year'] = result['date'].map(lambda x: x[0:4])
        result['date2'] = result['year'] + '-' + result['month'] + '-' + result['day']

        result['departure_time'] = result['date2'] + ' ' + result['departure_time']
        result['arrival_time'] = result['date2'] + ' ' + result['arrival_time']

        result['departure_time'] = result['departure_time'].apply(
            lambda x: x[:8] + (str(int(x[8:10]) + 1) if int(x[11:13]) >= 24 else x) + x[10:11] + str(
                int(x[11:13]) - 24) + x[
                                      13:] if int(
                x[11:13]) >= 24 else x)
        result['arrival_time'] = result['arrival_time'].apply(
            lambda x: x[:8] + (str(int(x[8:10]) + 1) if int(x[11:13]) >= 24 else x) + x[10:11] + str(
                int(x[11:13]) - 24) + x[
                                      13:] if int(
                x[11:13]) >= 24 else x)
        print("Processing completed")

        print("Converting strings to datatime")

        result['arrival_time'] = pd.to_datetime(result['arrival_time'], format="%Y-%m-%d %H:%M",
                                                infer_datetime_format=True)
        result['departure_time'] = pd.to_datetime(result['departure_time'], format="%Y-%m-%d %H:%M",
                                                  infer_datetime_format=True)
        print("Conversion completed")

        self.result = result
        if not path.exists("data/processed_data.csv"):
            result.to_csv("data/processed_data.csv", date_format="%Y-%m-%d %H:%M")
        else:
            print("data/processed_data.csv already exists")

    def load_data(self):
        self.result = pd.read_csv('data/processed_data.csv', parse_dates=['arrival_time', 'departure_time'], infer_datetime_format=True)

    def get_all_departures_from_bus_stop(self, stop_id: int, arrival_time: datetime):
        """
        Get all departures from specific bus stop

        :param stop_id: int
        :param arrival_time: datetime
        :return: all_deparutres
        """
        # time = datetime.strptime(arrival_time, '%Y-%m-%d %H:%M')
        time = arrival_time
        all_deparutres = self.result[(self.result["stop_id"] == stop_id) &
                                     (self.result['departure_time'] >= time) & (
                                             self.result['departure_time'] <= time + timedelta(hours=2)) &
                                     ~((self.result['drop_off_type'] == 0) & (self.result['pickup_type'] == 1))]
        return all_deparutres

    def trip_stops(self, trip_id: str, stop_id: int):
        """
        Get next bus stops from trip
        :param trip_id: str
        :param stop_id: int
        :return:
        """
        x = pd.DataFrame(self.result[self.result['trip_id'] == trip_id].sort_values(by=['stop_sequence']))
        x = x[x['stop_sequence'] >= x[x['stop_id'] == stop_id]['stop_sequence'].values[0]]
        stops = pd.concat(
            [x['route_id'], x['stop_id'], x['stop_name'], x['stop_lat'], x['stop_lon'], x['departure_time'],
             x['arrival_time']], axis=1)
        return stops

    def get_fastest_busses_from_bus_stop(self, stop_id: int, time: datetime):
        """
        Get 6 fastest busses from bus stop

        :param stop_id:
        :param time:
        :return:
        """
        tmp = self.get_all_departures_from_bus_stop(stop_id, time)
        trip_idser = tmp.sort_values(by=['departure_time'])['trip_id'].iloc[:6].reset_index(drop=True)
        a = pd.DataFrame()
        for i in range(0, len(trip_idser)):
            a = pd.concat([a, self.trip_stops(trip_idser[i], stop_id)])
        return a

    def trip_stops(self, trip_id, stop_id):
        x = pd.DataFrame(self.result[self.result['trip_id'] == trip_id].sort_values(by=['stop_sequence']))
        x = x[x['stop_sequence'] >= x[x['stop_id'] == stop_id]['stop_sequence'].values[0]]
        stops = pd.concat(
            [x['route_id'], x['stop_id'], x['stop_name'], x['stop_lat'], x['stop_lon'], x['departure_time'],
             x['arrival_time']], axis=1)
        return stops
