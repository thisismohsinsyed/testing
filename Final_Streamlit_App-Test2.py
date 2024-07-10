import streamlit as st
from PIL import Image
import cv2
import numpy as np
from Contours_Detection_And_Classification_of_Pm_10_Particles_Final_Test import process_image
from ROI_Extraction import extract_roi_from_image_array
import folium
from streamlit_folium import st_folium
import streamlit.components.v1 as components

st.title("Particle Analysis App")

# Step 1: JavaScript to fetch client-side geolocation
def get_geolocation():
    geolocation_js = """
    <script>
    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(showPosition, showError);
        } else { 
            window.parent.postMessage({type: 'streamlit:setComponentValue', value: 'Geolocation is not supported by this browser.'}, '*');
        }
    }
    function showPosition(position) {
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: [position.coords.latitude, position.coords.longitude]}, '*');
    }
    function showError(error) {
        var errorMessage = 'Unknown error';
        switch(error.code) {
            case error.PERMISSION_DENIED:
                errorMessage = "User denied the request for Geolocation."
                break;
            case error.POSITION_UNAVAILABLE:
                errorMessage = "Location information is unavailable."
                break;
            case error.TIMEOUT:
                errorMessage = "The request to get user location timed out."
                break;
            case error.UNKNOWN_ERROR:
                errorMessage = "An unknown error occurred."
                break;
        }
        window.parent.postMessage({type: 'streamlit:setComponentValue', value: errorMessage}, '*');
    }
    getLocation();
    </script>
    """
    components.html(geolocation_js, height=0)

if "geo_data" not in st.session_state:
    get_geolocation()
    st.session_state["geo_data"] = None

# Display received geolocation data or error
if st.session_state["geo_data"]:
    if isinstance(st.session_state["geo_data"], list):
        latitude, longitude = st.session_state["geo_data"]
        st.success(f"Your location has been automatically determined: Latitude {latitude}, Longitude {longitude}")
    else:
        st.error(st.session_state["geo_data"])

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
