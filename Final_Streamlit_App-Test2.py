import streamlit as st
from PIL import Image
import cv2
import numpy as np
from Contours_Detection_And_Classification_of_Pm_10_Particles_Final_Test import process_image
from ROI_Extraction import extract_roi_from_image_array
import folium
from streamlit_folium import st_folium
import geocoder
from datetime import date

st.title("Particle Analysis App")

# Step 0: User inputs for any date range
st.write("Please select the start and end dates for the experiment:")
start_date = st.date_input("Start date", value=date.today())
end_date = st.date_input("End date", value=date.today())

if start_date > end_date:
    st.error("End date must be after start date.")

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
        #results = process_image(cv2.cvtColor(roi, cv2.COLOR_RGB2BGR))
        #st.write("Particle Count:", results)

    # Step 1: Automatically fetch the user's latitude and longitude using their IP
    @st.cache(allow_output_mutation=True)
    def get_location():
        g = geocoder.ip('me')
        return g.latlng

    latlng = get_location()

    if latlng:
        st.session_state["latitude"], st.session_state["longitude"] = latlng
        st.success(f"Your location has been automatically determined: Latitude {latlng[0]}, Longitude {latlng[1]}")
    else:
        st.error("Could not determine your location automatically. Please ensure you have an internet connection.")

    # Step 3: Display Map with Pinpointed Location
    if "latitude" in st.session_state and "longitude" in st.session_state:
        m = folium.Map(location=[st.session_state["latitude"], st.session_state["longitude"]], zoom_start=12)
        folium.Marker([st.session_state["latitude"], st.session_state["longitude"]],
                      popup=f"Saved Location: Latitude {st.session_state['latitude']}, Longitude {st.session_state['longitude']}",
                      tooltip="Your location").add_to(m)
        st_folium(m, key='map')

    # Display the start and end dates to the user after all other operations
    st.write(f"Experiment Duration: Start Date - {start_date.strftime('%Y-%m-%d')}, End Date - {end_date.strftime('%Y-%m-%d')}")

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
