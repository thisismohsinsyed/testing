import os
import requests

# Fetch the Google Maps API key from the environment variable
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_location(city_name):
    """Retrieve the location data from Google Maps API based on city name."""
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={city_name}&key={API_KEY}"
    response = requests.get(url).json()
    if response['status'] == 'OK':
        return response['results'][0]['geometry']['location']
    else:
        return None

def create_map_html(lat, lng):
    """Generates HTML to embed Google Maps with a marker that updates position on click, supports 'Ctrl + scroll' to zoom, and updates hidden input fields."""
    return f"""
    <html>
    <head>
        <style>
            #map {{
                height: 400px;
                width: 100%;
            }}
        </style>
        <script src="https://maps.googleapis.com/maps/api/js?key={API_KEY}"></script>
        <script>
            var marker;  // Declare marker globally to update its position

            function initMap() {{
                var location = {{lat: {lat}, lng: {lng}}};
                var mapOptions = {{
                    zoom: 15,
                    center: location,
                    scrollwheel: true,  // Allow scrollwheel zooming
                    gestureHandling: 'auto'  // Allow 'Ctrl + scroll' for zooming
                }};
                var map = new google.maps.Map(document.getElementById('map'), mapOptions);
                
                marker = new google.maps.Marker({{
                    position: location,
                    map: map
                }});

                // Store initial position in hidden inputs
                document.getElementById('lat').value = {lat};
                document.getElementById('lng').value = {lng};

                // Add a click event listener to the map to update marker position
                map.addListener('click', function(e) {{
                    placeMarker(e.latLng, map);
                }});
            }}

            function placeMarker(latLng, map) {{
                marker.setPosition(latLng);  // Update marker position
                map.panTo(latLng);
                // Update hidden form values with new position
                document.getElementById('lat').value = latLng.lat();
                document.getElementById('lng').value = latLng.lng();
            }}
        </script>
    </head>
    <body onload="initMap()">
        <div id="map"></div>
        <input type='hidden' id='lat' name='lat'>
        <input type='hidden' id='lng' name='lng'>
    </body>
    </html>
    """

    """Generates HTML to embed Google Maps with a draggable marker that updates hidden input fields when moved."""
    return f"""
    <html>
    <head>
        <style>
            #map {{
                height: 400px;
                width: 100%;
            }}
        </style>
        <script src="https://maps.googleapis.com/maps/api/js?key={API_KEY}"></script>
        <script>
            var map, marker;

            function initMap() {{
                var initialLocation = {{lat: {lat}, lng: {lng}}};
                map = new google.maps.Map(document.getElementById('map'), {{
                    zoom: 15,
                    center: initialLocation,
                    scrollwheel: true,
                    gestureHandling: 'cooperative'
                }});

                marker = new google.maps.Marker({{
                    position: initialLocation,
                    map: map,
                    draggable: true,
                    title: "Drag me!"  // Tooltip on hover to indicate the marker is draggable
                }});

                // This event listener updates the position of the marker to the new location
                marker.addListener('dragend', function() {{
                    var position = marker.getPosition();
                    document.getElementById('lat').value = position.lat();
                    document.getElementById('lng').value = position.lng();
                }});
            }}
        </script>
    </head>
    <body onload="initMap()">
        <div id="map"></div>
        <input type='hidden' id='lat' name='lat' value='{lat}'>
        <input type='hidden' id='lng' name='lng' value='{lng}'>
    </body>
    </html>
    """
