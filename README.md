Travel Planner

A web application demonstrating graph algorithms (Dijkstra and Held–Karp TSP) for planning optimal travel routes between a sequence of cities, with support for three metrics: Fastest (minimize flight time), Cheapest (minimize cost), and Shortest (minimize great‑circle distance).

Features

  -Create and manage trips with a name, date range, and a list of cities
  
  -Persistence of trips in data/trips.json
  
  -Add/Remove locations interactively on the Add Locations page
  
  -Optimize the visit order of intermediate cities using:
  
  -Dijkstra’s algorithm (for time and cost)
  
  -Held–Karp dynamic programming (TSP)
  
  -Direct Haversine distance (for shortest path)
  
  -Interactive map via Google Maps JavaScript API
  
  -Flight legs drawn as red polylines with arrowhead symbols
  
  -Auto‑fit to bounds
  
  -Statistics displayed on the Route page:
  
  -Total distance (km)
  
  -Estimated time (h m)
  
  -Total cost (unitless dollars)
  
  -Algorithm execution time (ms)
  
  -Single‑page navigation using Flask + Jinja2 templates

Requirements

  -Python 3.7+
  -Flask
  -A Google Maps JavaScript API key
  
  Clone the Repository
    git clone <repo_url> travel-planner
    cd travel-planner
  Install Dependencies
    pip install -r requirements.txt
  Run python3 app.py
  Open your browser to http://127.0.0.1:5000/
 
Project Structure
  travel-planner/
├── app.py                # Flask application
├── graph.py              # Graph algorithms (Dijkstra, TSP, Haversine)
├── data/
│   ├── cities.csv        # City metadata
│   ├── routes.csv        # Route definitions
│   └── trips.json        # Persisted user trips
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── create_trip.html
│   ├── add_locations.html
│   └── route_display.html
├── static/
│   ├── css/style.css
│   └── js/maps.js
└── requirements.txt      # Python dependencies
