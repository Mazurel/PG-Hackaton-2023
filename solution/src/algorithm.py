from pathlib import Path
from datetime import time, timedelta, datetime
import math
from collections import deque

import numpy as np
import pandas as pd
from geopy.distance import geodesic 

from GTFS import load_data, prepare_data, get_fastest_busses_from_bus_stop

class Algorithm:
    def __init__(self):
        self.stops = self._load_stops_from_file()
        self.human_speed = 4
        self.time_delay = 2.5
        self.num_of_closest_stops_to_start = 5
        self.num_of_closest_stops = 20
        self.distance_criterion = 2
        self.max_stack_len = 10

        # Stack contains:
        #   - stop_id
        #   - route_id
        #   - arrival_time
        self.route_stack = deque()
        self.best_route = []
        self.best_time = time(23, 59)

    def get_route(self, point_A, point_B, **settings):
        """Create a route from point A to point B,
        based on settings passed to the function.
        
        Parameters
            point_A (tuple) - x, y coordinates of point A
            point_B (tuple) - x, y coordinates of point B
            settings (list) - additional settings: starting time, number of switches etc.
        """
        route = []

        # find closest stops in walking distance
        closest_stops = self._get_closest_stop(point_A, self.stops, self.num_of_closest_stops_to_start)

        for i in range(0, self.num_of_closest_stops):
            # get coords from stop id
            stop_coords = self._stop_id_to_coords(closest_stops[i])

            # calculate distance from and time to point_A to closest stop
            distance, walk_time = self._get_walking_distance(point_A, stop_coords)

            time_at_first_stop = self.time_to_stop(settings['start_time'], walk_time)

            self.route_stack.append([closest_stops[i], None,  time_at_first_stop])
            self._check_stop(closest_stops[i], point_A, point_B, time_at_first_stop)
            self.route_stack.pop()

    def _check_stop(self, stop_id, start_point, end_point, start_time):
        """Check available routes from current stop
        
        Parameters
            stop_id (int) - id of the stop that will be checked
            start_point (tuple) - x, y coordinates of the starting point
            end_point (tuple)
            start_time (datetime.time) - time at which the trip starts
        """
        if len(self.route_stack) > self.max_stack_len:
            return
        # get coords from stop id
        stop_coords = self._stop_id_to_coords(stop_id)

        # calculate distance from and time to point_A to closest stop
        distance, walk_time = self._get_walking_distance(stop_coords, end_point)

        if distance < self.distance_criterion:
            self.update_best_route(end_point, walk_time)

        # dataframe with all available routes from given stop
        all_routes = get_fastest_busses_from_bus_stop(stop_coords, start_time)
        print(all_routes.columns)
        closest_stops = self._get_closest_stop(end_point, all_routes, num_stops=self.num_of_closest_stops, return_all=True)

        #TODO: solve problem with time

        for i in range(self.num_of_closest_stops):
            self.route_stack.append([closest_stops[i, ['stop_id']], closest_stops[i, ['route_id']], closest_stops[i, ['stop_time']]])
            self._check_stop(
                closest_stops[i, ['stop_id']], 
                self._stop_id_to_coords(closest_stops[i, ['stop_id']]), 
                end_point, 
                closest_stops[i, ['stop_time']]
            )
            self.route_stack.pop()

    def update_best_route(self, end_point, walk_time):
        """Update currently best route based on stack"""
        current_route = list(self.route_stack)
        last_stop_arrival = current_route[-1][2]
        destination_arrival_time = self.time_to_stop(last_stop_arrival, walk_time)

        if destination_arrival_time.hour < self.best_time.hour or \
            (destination_arrival_time.hour == self.best_time.hour and destination_arrival_time.minute < self.best_time.minute):
            self.best_route = current_route
            self.best_time = destination_arrival_time

    def _check_routes(self, route, end_point):
        """Find stop along current route that is the closest to destination point
        
        Parameters
            route (DataFrame) - dataframe with all the stops along all routes
            end_point (tuple) - coordinates of destination point
        """

        closest_stops = self._get_closest_stop(end_point, route, num_stops=self.num_of_closest_stops)

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

        distance_with_ind = np.zeros((2, x.shape[0]))

        distance_with_ind[0] = np.square(np.square(y - base_y) + np.square(x - base_x))
        distance_with_ind[1] = np.array(stops['stop_id'])

        df = pd.DataFrame(distance_with_ind.T, columns=['distance', 'stop_id'])
        sorted = df.sort_values('distance')

        if return_all:
            return sorted.head(num_stops)
        return np.array(sorted.head(num_stops)['stop_id'], dtype=int)
        

    def _load_stops_from_file(self):
        """Load coordinates of all the stops from file"""

        file = Path("data/stops.txt")       
        return pd.read_csv(file).drop(columns=["stop_code", "stop_name"])

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
        lat = float(self.stops.loc[self.stops['stop_id'] == stop_id]['stop_lat'])
        lon = float(self.stops.loc[self.stops['stop_id'] == stop_id]['stop_lon'])
        return lat, lon 
    
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
    prepare_data()
    # load_data()
    algo = Algorithm()
    # print(algo.stops)
    algo.get_route((54.381709857835816, 18.591475549238343), (54.381709857835816, 18.591475549238343), start_time=datetime(2023, 1, 13, 21, 15))
