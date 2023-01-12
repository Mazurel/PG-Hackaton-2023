from pathlib import Path
import numpy as np
import pandas as pd

def get_next_stops_from_GTFS(point):
    pass

class Algorithm:
    def __init__(self):
        self.stops = self._load_stops_from_file()
        self._get_closest_stop((54.381309866159,18.604544291995))

    def get_route(self, point_A, point_B, *settings):
        """Create a route from point A to point B,
        based on settings passed to the function.
        
        Parameters
            point_A (tuple) - x, y coordinates of point A
            point_B (tuple) - x, y coordinates of point B
            settings (list) - additional settings: starting time, number of switches etc.
        """

        closest_stop = self._get_closest_stop(point_A)

        next_stops_with_routes = get_next_stops_from_GTFS(closest_stop)

    def _get_closest_stop(self, point, num_stops=5, return_distance=False):
        """Get closest stop to current coordinates
        
        Parameters
            point (tuple) - x, y coordinates of current position
            num_stops (int) - number of closest stops to specified point
            return_distance (bool) - flag that enables return of distance values
        
        Returns
            stop_id (np.array) - id of closest bus stop sorted from the closest"""
        
        x = np.array(self.stops["stop_lat"])
        y = np.array(self.stops["stop_lon"])

        assert x.shape == y.shape
        
        base_x = point[0] * np.ones_like(x)
        base_y = point[1] * np.ones_like(y)

        distance_with_ind = np.zeros((2, x.shape[0]))

        distance_with_ind[0] = np.square(np.square(y - base_y) + np.square(x - base_x))
        distance_with_ind[1] = np.array(self.stops.index)

        df = pd.DataFrame(distance_with_ind.T, columns=['distance', 'stop_id'])
        sorted = df.sort_values('distance')
        
        if return_distance:
            return np.array(sorted.head(num_stops).values)

        return np.array(sorted.head(num_stops)['stop_id'], dtype=int)
        

    def _load_stops_from_file(self):
        """Load coordinates of all the stops from file"""

        file = Path("data/stops.txt")       
        return pd.read_csv(file, index_col='stop_id').drop(columns=["stop_code", "stop_name"])


if __name__ == "__main__":
    algo = Algorithm()
