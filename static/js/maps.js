let map;

function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: { lat: 0, lng: 0 },
    zoom: 2
  });

  // fetch & draw
  const tripName = window.location.pathname.split('/').pop();
  fetchAndDisplayRoute(tripName);
}

async function fetchAndDisplayRoute(tripName) {
  const resp = await fetch(`/api/route/${tripName}`);
  const data = await resp.json();
  if (data.error) {
    document.getElementById('map').style.display = 'none';
    document.getElementById('route-info').innerHTML =
      `<p class="error">${data.error}</p>`;
    return;
  }
  if(data.ordered){
    document.getElementById('route-list').innerHTML =
    '<strong>Route:</strong> ' + data.ordered.join(' → ');
  }

  // Draw straight-line flight legs
  const pts = [data.origin, ...data.waypoints, data.destination];
  let totalKm = 0;
  const bounds = new google.maps.LatLngBounds();

  const arrowSymobol = {
    path: google.maps.SymbolPath.FORWARD_CLOSED_ARROW,
    scale: 3,
    strokeColor: '#FF0000',
  }

  for (let i = 0; i < pts.length - 1; i++) {
    const p1 = pts[i], p2 = pts[i + 1];
    new google.maps.Polyline({
      map,
      path: [p1, p2],
      strokeColor: '#FF0000',
      strokeOpacity: 0.8,
      strokeWeight: 2,
      icons: [{
        icon: arrowSymobol,
        offset: '50%',
        repeat : '120px'
      }]
    });
    bounds.extend(p1);
    bounds.extend(p2);
    totalKm += haversine(p1, p2);
  }

  map.fitBounds(bounds);

  // Display total distance
  document.getElementById('total-distance').textContent =
    totalKm.toFixed(1) + ' km';

  // Display estimated time
  const secs = data.total_time;
  const hours = Math.floor(secs / 3600);
  const mins = Math.floor((secs % 3600) / 60);
  document.getElementById('total-time').textContent =
    hours + 'h ' + mins + 'm';

  // Display total cost
  const cost = data.total_cost;
  document.getElementById('total-cost').textContent =
    "$" + cost.toFixed(2);
  // Display execution time
  const execTime = data.exec_time_ms;
  document.getElementById('exec-time').textContent =
    execTime.toFixed(4) + ' ms';
}

// Haversine formula
function haversine(a, b) {
  const toRad = x => x * Math.PI / 180;
  const R = 6371;
  const dLat = toRad(b.lat - a.lat);
  const dLon = toRad(b.lng - a.lng);
  const lat1 = toRad(a.lat), lat2 = toRad(b.lat);
  const sinDlat = Math.sin(dLat/2), sinDlon = Math.sin(dLon/2);
  const a1 = sinDlat*sinDlat +
             Math.cos(lat1)*Math.cos(lat2)*sinDlon*sinDlon;
  const c = 2 * Math.atan2(Math.sqrt(a1), Math.sqrt(1 - a1));
  return R * c;
}

window.initMap = initMap;
