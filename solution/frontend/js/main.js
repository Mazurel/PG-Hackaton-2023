const URL = "http://localhost:3000"

const latLngToCoords = (pos) => [
    pos.lat,
    pos.lng
]

const getCurrentTime = () => {
    const time_element = document.getElementById("current-time");
    const selected_date = time_element.valueAsDate;
    return {
        year: selected_date.getFullYear(),
        month: selected_date.getMonth() + 1,
        day: selected_date.getDate(),
        hour: selected_date.getHours(),
        minute: selected_date.getMinutes(),
    }
}

const startSearch = async (startingPoint, endingPoint) => {
    return (await fetch(`${URL}/api/search`, {
        method: "POST",
        mode: "cors",
        headers: {
            'Content-Type': "application/json"
        },
        body: JSON.stringify({
            "starting_point": startingPoint,
            "ending_point": endingPoint,
            "settings": {
                "time": getCurrentTime()
            }
        })
    })).text()
}

const getSearchResult = (id) => new Promise((resolve, reject) => {
    const TIMEOUT_MAX = 500;
    const QUERY_TIME = 50;
    const MAX_COUNT = Math.floor(TIMEOUT_MAX / QUERY_TIME);

    let count = 0;
    interval = setInterval(() => {
        fetch(`${URL}/api/query/${id}`, {
            method: "GET",
            mode: "cors",
        }).then((res) => {
            res.json()
                .then((data) => {
                    clearInterval(interval);
                    resolve(data.points);
                })
        })
        count += 1;
        if (count > MAX_COUNT) {
            clearInterval(interval);
            reject("Timeout");
        }
    }, QUERY_TIME)
})


class MapController {
    constructor() {
        this._starting_marker = null;
        this._ending_marker = null;
        this._connection_lines = []
        this._checkpoints = []
        this._next_first = true;
    }

    initialize_map() {
        this.map = L.map('map', {
            fullscreenControl: true,
        }).setView([54.36, 18.636], 11);

        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        }).addTo(this.map);

        this.map.on("click", (ev) => {
            this.set_next_pos(latLngToCoords(ev.latlng));
            this.clear();
            this.update();
        })
    }

    clear() {
        this._connection_lines.forEach(line => line.remove());
        this._connection_lines = [];
        this._checkpoints.forEach(chkpt => chkpt.remove());
        this._checkpoints = []
    }

    async update() {
        if (this.start_position != null && this.end_position != null) {
            const id = await startSearch(this.start_position, this.end_position)
            console.log(id)
            return
            const points = await getSearchResult(id);

            this._checkpoints = points.map((pt) => L.marker(pt).addTo(this.map).bindPopup(pt.name));

            let polys = [];
            for (let i = 0; i < points.length - 1; i++) {
                polys.push([
                    points[i],
                    points[i + 1]
                ])
            }

            this._connection_lines = polys.map(pl => L.polyline(pl).addTo(this.map))
        }
    }

    set start_position(pos) {
        if (!Array.isArray(pos) && pos.length != 2) throw Error("Invalid arguments !")

        if (this._starting_marker instanceof L.Marker) {
            this._starting_marker.remove()
        }
        this._starting_marker = L.marker().setLatLng(pos).addTo(this.map);
    }

    get start_position() {
        return this._starting_marker ? latLngToCoords(this._starting_marker.getLatLng()) : null;
    }

    set end_position(pos) {
        if (!Array.isArray(pos) && pos.length != 2) throw Error("Invalid arguments !")

        if (this._ending_marker instanceof L.Marker) {
            this._ending_marker.remove()
        }
        this._ending_marker = L.marker().setLatLng(pos).addTo(this.map);
    }

    get end_position() {
        return this._ending_marker ? latLngToCoords(this._ending_marker.getLatLng()) : null;
    }

    set_next_pos(pos) {
        if (this._next_first) {
            this.start_position = pos;
        }
        else {
            this.end_position = pos;
        }

        this._next_first = !this._next_first;
    }
}

const mapController = new MapController()

document.onreadystatechange = () => {
    if (document.readyState != "complete") return;
    mapController.initialize_map()
    const time_element = document.getElementById("current-time");
    const date = new Date();
    date.setSeconds(0);
    date.setMilliseconds(0);
    time_element.valueAsDate = date

    setInterval(mapController.update, 500);
}
