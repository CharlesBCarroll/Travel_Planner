import os
import json
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from graph import Graph
from math import isinf
import time

app = Flask(__name__)

# File for persisting trips
TRIPS_FILE = 'data/trips.json'


def load_trips():
    if os.path.exists(TRIPS_FILE):
        with open(TRIPS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_trips():
    os.makedirs(os.path.dirname(TRIPS_FILE), exist_ok=True)
    with open(TRIPS_FILE, 'w') as f:
        json.dump(trips, f, indent=2)

# Initialize graph from CSV data
global_graph = Graph('data/cities.csv', 'data/routes.csv')

# Load persisted trips or start empty
trips = load_trips()

@app.route('/')
def home():
    return render_template('index.html', trips=trips)

@app.route('/create-trip', methods=['GET', 'POST'])
def create_trip():
    error = None
    if request.method == 'POST':
        name = request.form['name'].strip()
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        preference = request.form.get('preference', 'time')
        if name in trips:
            error = f"Trip '{name}' already exists. Choose a different name."
        else:
            trips[name] = {
                'start_date': start_date,
                'end_date': end_date,
                'locations': [],
                'preference': preference
            }
            save_trips()
            return redirect(url_for('add_locations', trip_name=name))
    return render_template('create_trip.html', error=error)

@app.route('/add-locations/<trip_name>', methods=['GET', 'POST'])
def add_locations(trip_name):
    if trip_name not in trips:
        abort(404)
    error = None

    if request.method == 'POST':
        # If they clicked “Finish Trip”, skip validation and go to the map
        if 'finish' in request.form:
            return redirect(url_for('route_page', trip_name=trip_name))
        # If they clicked “Delete Trip”, remove it and redirect to home
        if 'remove' in request.form:
            loc_to_remove = request.form['remove']
            if loc_to_remove in trips[trip_name]['locations']:
                trips[trip_name]['locations'].remove(loc_to_remove)
                save_trips()
            return redirect(url_for('add_locations', trip_name=trip_name))
        # Otherwise it's the Add button: validate & save the city
        loc = request.form.get('location', '').strip()
        if not loc:
            error = "Please enter a city name to add."
        elif loc not in global_graph.locations:
            error = f"City '{loc}' not found. Please enter a supported city."
        elif loc in trips[trip_name]['locations']:
            error = f"City '{loc}' already added."
        else:
            trips[trip_name]['locations'].append(loc)
            save_trips()

    return render_template(
        'add_locations.html',
        trip_name=trip_name,
        locations=trips[trip_name]['locations'],
        error=error
    )


@app.route('/route/<trip_name>')
def route_page(trip_name):
    if trip_name not in trips:
        abort(404)
    locs = trips[trip_name]['locations']
    error = None
    if len(locs) < 2:
        error = "Please add at least two cities to view a route."
    return render_template(
        'route_display.html',
        trip_name=trip_name,
        start_date=trips[trip_name]['start_date'],
        end_date=trips[trip_name]['end_date'],
        preference=trips[trip_name]['preference'],
        error=error
    )

@app.route('/api/route/<trip_name>')
def route_api(trip_name):
    start = time.perf_counter()
    if trip_name not in trips:
        abort(404)

    city_list = trips[trip_name]['locations']
    if len(city_list) < 2:
        return jsonify({
            'origin': None,
            'waypoints': [],
            'destination': None,
            'total_time': 0,
            'total_cost': 0
        })

    # Choose weighting based on user preference
    pref = trips[trip_name]['preference']
    if pref == 'cost':
        weight = 'cost'
    elif pref == 'distance':
        weight = 'distance'
    else:
        weight = 'time'

    # Compute TSP ordering, catch if no full tour is possible
    try:
        ordered = global_graph.tsp_path(city_list, weight=weight)
    except ValueError as e:
        return jsonify({'error': str(e)})

    # Verify connectivity between each consecutive pair
    for a, b in zip(ordered, ordered[1:]):
        if isinf(global_graph.shortest_distance(a, b, weight)):
            return jsonify({
                'error': f"No route found between {a} and {b}. Please remove or replace one of these cities."
            })

    # Build list of coordinate objects
    coords = [
        {
            'lat': global_graph.locations[name].lat,
            'lng': global_graph.locations[name].lon
        }
        for name in ordered
    ]

    # Sum up flight time for each leg
    total_time_hours = sum(
        global_graph.shortest_distance(a, b, weight='time')
        for a, b in zip(ordered, ordered[1:])
    )
    # Convert to seconds
    total_time_seconds = int(total_time_hours * 3600)

    # Sum up cost for each leg
    total_cost = sum(
        global_graph.shortest_distance(a, b, weight='cost')
        for a, b in zip(ordered, ordered[1:])
    )

    exec_time_ms = (time.perf_counter() - start) * 1000.0

    return jsonify({
        'origin':      coords[0],
        'waypoints':   coords[1:-1],
        'destination': coords[-1],
        'total_time':  total_time_seconds,
        'total_cost':  total_cost,
        'ordered':      ordered,
        'exec_time_ms': exec_time_ms
    })


def delete_trip(trip_name):
    if trip_name in trips:
        trips.pop(trip_name)
        save_trips()
    return redirect(url_for('home'))

@app.route('/delete-trip/<trip_name>', methods=['POST'])
def handle_delete_trip(trip_name):
    return delete_trip(trip_name)

if __name__ == '__main__':
    app.run(debug=True)
