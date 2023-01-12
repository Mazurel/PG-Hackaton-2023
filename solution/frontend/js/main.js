const latLngToCoords = (pos) => [
    pos.lat,
    pos.lng
]

class MapController {
    constructor() {
        this._starting_marker = null;
        this._ending_marker = null;
        this._connection_lines = []
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
            this.update();
        })
    }

    update() {
        if (this.start_position != null && this.end_position != null) {
            this._connection_lines.map((line) => {
                line.remove()
            })

            this._connection_lines = [L.polyline([
                this.start_position,
                this.end_position
            ])
            ]
            this._connection_lines.forEach((line) => line.addTo(this.map))
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
    mapController.start_position = [54.357652, 18.658762]
    mapController.end_position = [54.381310, 18.604082]
    mapController.update()
}
