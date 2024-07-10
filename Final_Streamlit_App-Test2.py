import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import cv2
import numpy as np
from Contours_Detection_And_Classification_of_Pm_10_Particles_Final_Test import process_image
from ROI_Extraction import extract_roi_from_image_array
import folium
from streamlit_folium import st_folium

st.title("Particle Analysis App")

# JavaScript to fetch client-side geolocation
def get_geolocation():
    geolocation_js = """
    <script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(showPosition, showError);
        } else {
            document.getElementById('geolocation').innerHTML = "Geolocation is not supported by this browser.";
        }
    }
    function showPosition(position) {
        document.getElementById('geolocation').innerHTML = "Latitude: " + position.coords.latitude + 
        "<br>Longitude: " + position.coords.longitude;
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: [position.coords.latitude, position.coords.longitude]
        }, '*');
    }
    function showError(error) {
        switch(error.code) {
            case error.PERMISSION_DENIED:
                document.getElementById('geolocation').innerHTML = "User denied the request for Geolocation."
                break;
            case error.POSITION_UNAVAILABLE:
                document.getElementById('geolocation').innerHTML = "Location information is unavailable."
                break;
            case error.TIMEOUT:
                document.getElementById('geolocation').innerHTML = "The request to get user location timed out."
                break;
            default:
                document.getElementById('geolocation').innerHTML = "An unknown error occurred."
                break;
        }
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'Error'}, '*');
    }
    getLocation();
    </script>
    <div id="geolocation">Waiting for location...</div>
    """
    components.html(geolocation_js, height=100)

# Fetch and display geolocation
if "geo_data" not in st.session_state:
    get_geolocation()

if "geo_data" in st.session_state and st.session_state["geo_data"] != 'Error':
    if isinstance(st.session_state["geo_data"], list):
        latitude, longitude = st.session_state["geo_data"]
        st.success(f"Location obtained: Latitude {latitude}, Longitude {longitude}")
    elif st.session_state["geo_data"] == 'Error':
        st.error("Error fetching geolocation.")
else:
    st.warning("Location not yet available or permission denied.")

# Step 2: Image Upload and Processing
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
if uploaded_file is not None:
    image = Image.open(uploaded_file).convert("RGB")
    image_array = np.array(image)
    image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR for OpenCV

    image_with_contour, roi = extract_roi_from_image_array(image_array)
    if image_with_contour is not None:
        st.image(image_with_contour, caption='Detected Inner Square From Input Image', use_column_width=True)
    if roi is not None:
        st.image(roi, caption='Detected Region Of Interest', use_column_width=True)
        results = process_image(cv2.cvtColor(roi, cv2.COLOR_RGB2BGR))
        st.write("Particle Count:", results)

    # Step 3: Display Map with Pinpointed Location if geolocation was successful
    if isinstance(st.session_state.get("geo_data"), list):
        m = folium.Map(location=[latitude, longitude], zoom_start=12)
        folium.Marker([latitude, longitude], popup=f"Saved Location: Latitude {latitude}, Longitude {longitude}", tooltip="Your location").add_to(m)
        st_folium(m, key='map')

# Reference table for air pollution analysis
st.write("Reference Table for Air Pollution Analysis")
reference_data = {
    "Description": [
        "The paper has many black and grey dots. Large parts of the paper have turned grey.",
        "The paper has quite a few black and grey dots. There are some parts on the paper that have turned grey.",
        "The paper has black and grey dots all over the surface, but there are no fields that are completely grey.",
        "The paper has only a few black and grey dots, and there are no fields that are completely grey."
    ],
    "Dots per cm²": ["> 50", "26 - 50", "11 - 25", "< 11"],
    "Air pollution level": ["Very high", "High", "Medium", "Low"]
}
st.table(reference_data)
