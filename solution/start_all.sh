#!/usr/bin/env bash

sh frontend/run_frontend.sh &
FRONTEND_PID=$?
flask --app backend run --port 3000 &
BACKEND_PID=$?

exit_all() {
    kill $FRONTEND_PID
    kill $BACKEND_PID
}

trap "exit_all" INT

echo "Starting WebApp, type http://localhost:8000/ to open it !"

sleep 1s

python -c "import webbrowser; webbrowser.open('http://localhost:8000/')"

while [ 1 ]; do
    read
done