import streamlit as st
from PIL import Image
import cv2
import numpy as np
from Contours_Detection_And_Classification_of_Pm_10_Particles_Final_Test import process_image
from ROI_Extraction import extract_roi_from_image_array
import folium
from streamlit_folium import st_folium
import geocoder
from location_locator import get_location, create_map_html
from datetime import date

# Set page configuration and theme related to air pollution
st.set_page_config(page_title="Air Pollution Particle Analysis", layout="wide")
st.markdown(
    """
    <style>
    .main {
        background-color: #FFFFFF;
    }
    h1 {
        color: #333;
    }
    .stTextInput, .stDateInput, .stButton, .stFileUploader {
        margin: 10px 0;
    }
    .reportview-container .main footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

# App title and description
st.title("Air Pollution Particle Analysis App")
st.markdown("""
This application helps to monitor and analyze air quality by detecting particulate matter from uploaded images. Please follow the steps below to perform the analysis.
""")

# Date input for experiment range
st.write("## Step 1: Experiment Date Range")
col1, col2 = st.columns(2)
with col1:
    start_date = st.date_input("Start date", value=date.today())
with col2:
    end_date = st.date_input("End date", value=date.today())

if start_date > end_date:
    st.error("End date must be after start date.")

# Location input and map display
st.write("## Step 2: Enter Location for Analysis")
city_name = st.text_input('Location:', '')
if city_name:
    location = get_location(city_name)
    if location:
        html_string = create_map_html(location['lat'], location['lng'])
        st.components.v1.html(html_string, height=450)
        if st.button("Locate"):
            st.success('Coordinates located!')
            st.text_input("Latitude", value=location['lat'])
            st.text_input("Longitude", value=location['lng'])
    else:
        st.error("City not found. Please enter a valid city name.")

# Image upload and processing
st.write("## Step 3: Upload Image for Analysis")
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

# Reference table for air pollution analysis
st.write("## Reference Table for Air Pollution Analysis")
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












