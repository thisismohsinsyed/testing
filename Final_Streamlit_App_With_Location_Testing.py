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
import time 
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import streamlit.components.v1 as components

# Set page configuration and theme related to air pollution
st.set_page_config(page_title="Air Pollution Particle Analysis", layout="wide")
st.markdown("""
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
        components.html(html_string, height=450)
        if st.button("Locate"):
            # Access the updated coordinates
            lat = float(st.session_state.get('lat', location['lat']))
            lng = float(st.session_state.get('lng', location['lng']))
            st.success(f'Coordinates located! Latitude: {lat}, Longitude: {lng}')
            st.text_input("Latitude", value=lat)
            st.text_input("Longitude", value=lng)
    else:
        st.error("City not found. Please enter a valid city name.")
# Load model function
@st.cache_resource
def load_model():
    model = tf.keras.models.load_model('model.h5')
    return model
model = load_model()

def predict_image(model, image_file):
    with st.spinner('Classifying...'):
        progress_bar = st.progress(0)  # Initialize progress bar at 0%
        img = load_img(image_file, target_size=(150, 150))
        progress_bar.progress(25)  # Update progress bar after loading image
        img_array = img_to_array(img)
        img_array = img_array / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        prediction = model.predict(img_array)
        progress_bar.progress(50)  # Update progress bar after processing image to array
        label = int(prediction.round())
        progress_bar.progress(75)  # Update progress bar after prediction
        progress_bar.progress(100)  # Complete the progress bar
        time.sleep(2)  # Briefly display completed progress bar
    return label

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
if uploaded_file is not None:
    image = load_img(uploaded_file)
    st.image(image, caption='Uploaded Image.', width=600)
    label = predict_image(model, uploaded_file)
    if label == 0:
        st.error("Wrong Image Uploaded- I am expecting an Image of Air Meter Sensor, please upload again.")
    else:
        st.success("Classification Done: Air Meter Image Detected!")
        st.markdown("### Now Detecting ROI From Uploaded Image...")
        # Simulate ROI detection processing
        progress = st.progress(0)
        for i in range(100):
            time.sleep(0.02)
            progress.progress(i + 1)
        time.sleep(2)  # Simulate processing time
        image = Image.open(uploaded_file).convert("RGB")
        image_array = np.array(image)
        image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR for OpenCV
        from ROI_Extraction import extract_roi_from_image_array  # Ensure import is placed correctly
        image_with_contour, roi = extract_roi_from_image_array(image_array)
        if image_with_contour is not None:
            st.image(image_with_contour, caption='Detected Inner Square From Input Image', width=600)
        if roi is None:
            st.markdown("### No ROI Detected-Image Quality is Very Low.Plz Upload Good Quality Image")
        if roi is not None:
            st.image(roi, caption='Detected Region Of Interest', width=600)
            st.markdown("### Now Counting Particles...")
            # Initialize and display progress bar for particle counting
            progress = st.progress(0)
            for i in range(100):
                time.sleep(0.02)
                progress.progress(i + 1)
            time.sleep(3)  # Simulate additional processing time
            from Contours_Detection_And_Classification_of_Pm_10_Particles_Final_Test import process_image
            results = process_image(cv2.cvtColor(roi, cv2.COLOR_RGB2BGR))
            st.markdown("### Particles Counted Successfully!")
            st.write("Particle Count:", results)
            st.success("Particles detected successfully!")

# Reference table for air pollution analysis
st.write("## Reference Table for Air Pollution Analysis From NILU")
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
