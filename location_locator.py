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
    """Generates HTML to embed Google Maps with a marker and enables clicking on the map to get coordinates."""
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
            function initMap() {{
                var location = {{lat: {lat}, lng: {lng}}};
                var map = new google.maps.Map(document.getElementById('map'), {{
                    zoom: 15,
                    center: location
                }});
                var marker = new google.maps.Marker({{
                    position: location,
                    map: map
                }});

                // Add a click event listener to the map
                map.addListener('click', function(e) {{
                    placeMarkerAndPanTo(e.latLng, map);
                }});
            }}

            // Function to place a marker and pan to the new location
            function placeMarkerAndPanTo(latLng, map) {{
                var marker = new google.maps.Marker({{
                    position: latLng,
                    map: map
                }});
                map.panTo(latLng);
                alert('Lat: ' + latLng.lat() + '\\nLng: ' + latLng.lng());  // Display coordinates in an alert
            }}
        </script>
    </head>
    <body onload="initMap()">
        <div id="map"></div>
    </body>
    </html>
    """
