from pathlib import Path
from datetime import time, timedelta, datetime
import math
from collections import deque

import numpy as np
import pandas as pd
from geopy.distance import geodesic 


class Algorithm:
    def __init__(self, gtfs):
        self.stops = self._load_stops_from_file()
        self.human_speed = 4
        self.time_delay = 2.5
        self.num_of_closest_stops_to_start = 5
        self.num_of_closest_stops = 10
        self.distance_criterion = 1
        self.max_stack_len = 5

        # Stack contains:
        #   - stop_id
        #   - route_id
        #   - arrival_time
        self.route_stack = []
        self.best_route = []
        self.best_time = 1e18

        self.gtfs = gtfs
        self.kill = False


    def get_route(self, point_A, point_B, **settings):
        """Create a route from point A to point B,
        based on settings passed to the function.
        
        Parameters
            point_A (tuple) - x, y coordinates of point A
            point_B (tuple) - x, y coordinates of point B
            settings (list) - additional settings: starting time, number of switches etc.
        """

        self.gtfs.apply_time_limit(settings['start_time'], 12)

        # find closest stops in walking distance
        closest_stops = self._get_closest_stop(point_A, self.stops, self.num_of_closest_stops_to_start)

        for i in range(closest_stops.shape[0]):
            if self.kill:
                return
            # get coords from stop id
            stop_coords = self._stop_id_to_coords(closest_stops[i])

            # calculate distance from and time to point_A to closest stop
            distance, walk_time = self._get_walking_distance(point_A, stop_coords)

            time_at_first_stop = self.time_to_stop(settings['start_time'], walk_time)

            self.route_stack.append([closest_stops[i], None,  time_at_first_stop, []])
            self._check_stop(closest_stops[i], point_A, point_B, time_at_first_stop)
            self.route_stack.pop()
            
        print(f"Best route: {self.best_route}, best time: {self.best_time}")

    def _check_stop(self, stop_id, start_point, end_point, start_time, ):
        """Check available routes from current stop
        
        Parameters
            stop_id (int) - id of the stop that will be checked
            start_point (tuple) - x, y coordinates of the starting point
            end_point (tuple)
            start_time (datetime.time) - time at which the trip starts
        """
        if self.kill:
            return
        if len(self.route_stack) > self.max_stack_len:
            return

        # get coords from stop id
        stop_coords = self._stop_id_to_coords(stop_id)

        # calculate distance from and time to point_A to closest stop
        distance, walk_time = self._get_walking_distance(stop_coords, end_point)

        if distance < self.distance_criterion:
            self.update_best_route(end_point, walk_time)

        # dataframe with all available routes from given stop
        all_routes = self.gtfs.get_fastest_busses_from_bus_stop(stop_id, start_time)
        if all_routes.empty:
            return
        closest_stops = self._get_closest_stop(end_point, all_routes, num_stops=self.num_of_closest_stops, return_all=True)
        closest_stops = self._get_unique(closest_stops)

        if int(closest_stops.loc[0, ['stop_id']].values[0]) == stop_id:
            return

        for i in range(closest_stops.shape[0]):
            route_id = closest_stops.loc[i, ['route_id']].values[0]
            self.route_stack.append([
                int(closest_stops.loc[i, ['stop_id']].values[0]),
                int(route_id),
                closest_stops.loc[i, ['arrival_time']].values[0],
                all_routes[all_routes['route_id'] == route_id]])
            
            # print(f"stack size: {len(self.route_stack)}")

            self._check_stop(
                int(closest_stops.loc[i, ['stop_id']].values[0]), 
                self._stop_id_to_coords(int(closest_stops.loc[i, ['stop_id']].values[0])), 
                end_point, 
                closest_stops.loc[i, ['arrival_time']].values[0]
            )
            self.route_stack.pop()
    
    def _get_unique(self, stops):
        """Get unique routes"""
        ids = pd.unique(stops['stop_id'])
        rows = []
        for id in ids:
            same_id = stops[stops['stop_id'] == id]
            rows.append(same_id[same_id['level_0'] == same_id['level_0'].min()])
        return pd.concat(rows, axis=0).reset_index(drop=True)

    def update_best_route(self, end_point, walk_time):
        """Update currently best route based on stack"""
        current_route = list(self.route_stack)
        last_stop_arrival = current_route[-1][2]
        destination_arrival_time = self.time_to_stop(last_stop_arrival, walk_time)
        staring_point_time = current_route[0][2]
        route_time = destination_arrival_time - staring_point_time
        print(f"Found possible route, route_time: {route_time}")
        if route_time.seconds / 60  < self.best_time:
            self.best_route = self.prepare_best_route(current_route)
            self.best_time = route_time.seconds / 60
            print(f"updating best route, best route: {self.best_route}, best time: {self.best_time}")

    def prepare_best_route(self, current_route):
        """best route - [lat, lon, name, datetime]"""
        best_route = []
        first_stop = current_route[0][0]
        first_lat, first_lon = self._stop_id_to_coords(first_stop)
        first_name = self._stop_id_to_name(first_stop)
        # best_route.append([first_lat, first_lon, first_name, current_route[0][2]])

        for point in current_route[1:]:
            route = point[3].reset_index(drop=True)
            last_ind = int(route[route['stop_id'] == point[0]].index.values)
            best_route.append(route.iloc[:last_ind+1])

        final = pd.concat(best_route, axis=0)
        # print(final)
        return final

    def get_best_route(self):
        if len(self.best_route) <= 0:
            return []

        return [self._stop_id_to_coords(route[0]) for route in self.best_route]

    def _stop_id_to_name(self, stop_id):
        # print(self.stops.columns)
        name = self.stops.loc[self.stops['stop_id'] == int(stop_id), ['stop_name']].values[0]
        return name

    def _get_closest_stop(self, point, stops, num_stops=1, return_all=False):
        """Get closest stop to specified point
        
        Parameters
            point (tuple) - x, y coordinates of current position
            stops (DataFrame) - dataframe with coordinates of stops, required columns: stop_id, stop_lat, stop_lon
            num_stops (int) - number of closest stops to specified point
        
        Returns
            stop_id (np.array) - id of closest bus stop sorted from the closest"""
        
        x = np.array(stops["stop_lat"])
        y = np.array(stops["stop_lon"])

        assert x.shape == y.shape
        
        base_x = point[0] * np.ones_like(x)
        base_y = point[1] * np.ones_like(y)
        # if return_all:
        #     distance_with_ind = np.zeros((4, x.shape[0]))
        # else:
        distance_with_ind = np.zeros((2, x.shape[0]))

        distance_with_ind[0] = np.sqrt(np.square(y - base_y) + np.square(x - base_x))
        distance_with_ind[1] = np.array(stops['stop_id'])

        if return_all:
            # distance_with_ind[2] = np.array(stops['route_id'])
            # distance_with_ind[3] = np.array(stops['arrival_time'])
            df = pd.DataFrame(distance_with_ind.T, columns=['distance', 'stop_id'])
            df = pd.concat([df, stops.loc[:,['route_id','arrival_time']].reset_index()], axis=1)
        else:
            df = pd.DataFrame(distance_with_ind.T, columns=['distance', 'stop_id'])
        sorted = df.sort_values('distance')

        if return_all:
            return sorted.head(num_stops).reset_index()
        return np.array(sorted.head(num_stops)['stop_id'], dtype=int)
        

    def _load_stops_from_file(self):
        """Load coordinates of all the stops from file"""

        file = Path("data/stops.txt")       
        return pd.read_csv(file).drop(columns=["stop_code"])

    def _get_walking_distance(self, start, stop):
        """Get distance between two points
        
        Parameters
            start (tuple) - x, y coordinates of first point
            stop (tuple) - x, y coordinates of second point
        
        Return
            distance (float) - value of distance between two points in kilometers
            time (float) - time needed to walk between the points in hours
        """
        distance = geodesic(start, stop).kilometers
        time = distance / self.human_speed # in hours

        return distance, time

    def _stop_id_to_coords(self, stop_id):
        """Get stop coordinates based on stop_id
        
        Parameters
            stop_id (int) - stop id
            
        Returns
            (lat, lon) (tuple) - coordinates of the stop
        """
        coords = self.stops.loc[self.stops['stop_id'] == int(stop_id), ['stop_lat', 'stop_lon']].values.squeeze()
        return coords[0], coords[1]
    
    def time_to_stop(self, start_time, walking_time):
        """Add time to current time
        
        Parameters
            start_time (datetime.time) - trip start time
            walking_time (float) - walking time to closest stop in hours
            
        Returns
            at_stop_time (datetime.time) - time to start the journey from stop
            
        """

        add_minutes = math.ceil((walking_time * 60 + self.time_delay) % 60)
        add_hours = math.floor((walking_time * 60 + self.time_delay) / 60)
        
        return start_time + timedelta(hours=add_hours, minutes=add_minutes)

if __name__ == "__main__":
    # gtfs = GTFS()
    # gtfs.load_data()
    algo = Algorithm()

    # mandu -> gb
    # algo.get_route((54.40929967790238, 18.56702765741272), (54.381658077872665, 18.60563893543294), start_time=datetime(2023, 1, 13, 21, 15))
    # mandu -> hala oliwia
    algo.get_route((54.40929967790238, 18.56702765741272), (54.37604412817031, 18.614456596172488), start_time=datetime(2023, 1, 13, 21, 15))

    # algo.get_route((54.40929967790238, 18.56702765741272), (54.40929967790238, 18.56802765741272), start_time=datetime(2023, 1, 13, 21, 15))
