from flask import Flask, request, abort
from flask_cors import CORS

from threading import Thread
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
import time

from GTFS import GTFS
from algorithm import Algorithm

gtfs = GTFS()
gtfs.load_data()

app = Flask(__name__)
CORS(app)

@dataclass
class Point:
    lat: float
    lng: float
    name: str

    @staticmethod
    def from_coords(coords: tuple[float, float], name: str):
        return Point(
            lat=coords[0],
            lng=coords[1],
            name=name
        )

    def to_dict(self):
        return {
            "lat": self.lat,
            "lng": self.lng,
            "name": self.name
        }

@dataclass
class Result:
    processing: bool
    kill_thread: Optional[callable] = None
    get_data: Optional[callable] = None


results: dict[int, Result] = {}

def start_processing(starting_point: tuple[float, float],
                     ending_point: tuple[float, float],
                     settings: dict) -> int:
    '''
    Start background search.
    Modifies global `results` variable !
    Returns new processing id.
    '''
    global results
    def process():
        time.sleep(0.1)
        algo = Algorithm(gtfs)

        def get_points():
            if len(algo.best_route) == 0:
                return None
            res = [Point.from_coords(starting_point, "Starting Point")]
            for lat, lon, name, arrr, route in algo.best_route[["stop_lat", "stop_lon", "stop_name", "arrival_time", "route_id"]].values.tolist():
                res.append(Point.from_coords((lat, lon), f"{route} - {name}</br>{arrr}"))
            res.append(Point.from_coords(ending_point, "Ending Point"))
            return res
        
        def kill_thread():
            algo.kill = True

        current_result.get_data = get_points
        current_result.kill_thread = kill_thread

        current_time = datetime(
            year = settings["time"]["year"],
            month = settings["time"]["month"],
            day = settings["time"]["day"],
            hour = settings["time"]["hour"],
            minute = settings["time"]["minute"]
        )
        print("Started looking for best route !")
        algo.get_route(starting_point, ending_point, start_time=current_time)
        current_result.processing = False

    try:
        next_id = max(results.keys()) + 1
    except ValueError:
        next_id = 0
    current_result = Result(
        processing=True,
        get_data=None
    )
    Thread(target=process).start()

    results[next_id] = current_result
    return next_id


@app.route("/api/search", methods=["POST"])
def search_points():
    '''
    Start most optimal path search between two points specified by:
    - data["starting_point"] - We start from this point.
    - data["ending_point"] - We want to arrive at this point.
    - data["settings"] - Additional settings.
    '''
    data = request.get_json()
    try:
        starting_point = data["starting_point"]
        ending_point = data["ending_point"]
        settings = data["settings"]
        index = start_processing(starting_point, ending_point, settings)
        if index >= 1:
            print("Killing old thread !")
            results[index - 1].kill_thread()

        return str(index)
    except KeyError as err:
        abort(400, f"'{err}' argument was not specified.")


@app.route("/api/query/<index>", methods=["GET"])
def query_points(index: str):
    '''
    Query most optimal path, started by `/api/search` POST request.
    '''
    global results
    try:
        result = results[int(index)]
        data = result.get_data()
        return {
            "processing": result.processing,
            "points": [ point.to_dict() for point in data ] if data is not None else []
        }
    except KeyError as err:
        abort(400, f"'{err}' was not queried before.")
