from flask import Flask, request, abort
from flask_cors import CORS

from threading import Thread
from dataclasses import dataclass
from typing import Optional
from datetime import datetime

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
    points: Optional[list[Point]]


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
        # TODO: Optimize here !
        current_time = datetime(
            year = settings["time"]["year"],
            month = settings["time"]["month"],
            day = settings["time"]["day"],
            hour = settings["time"]["hour"],
            minute = settings["time"]["minute"]
        )
        print(current_time)
        current_result.processing = False
        current_result.points = [
            Point.from_coords(starting_point, "Starting Point"),
            Point.from_coords(((starting_point[0] + ending_point[0]) / 2 + 0.01, (starting_point[1] + ending_point[1]) / 2), "Man in the middle"),
            Point.from_coords(ending_point, "Ending Point")
        ]

    try:
        next_id = max(results.keys()) + 1
    except ValueError:
        next_id = 0
    current_result = Result(
        processing=True,
        points=None
    )
    Thread(target=process).run()

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
        return str(start_processing(starting_point, ending_point, settings))
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
        return {
            "processing": result.processing,
            "points": [ point.to_dict() for point in result.points ]
        }
    except KeyError as err:
        abort(400, f"'{err}' was not queried before.")
