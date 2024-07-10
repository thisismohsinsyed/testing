import cv2
import numpy as np

def upscale_image(image, method='inter_cubic'):
    """
    Upscales the image to a specific total number of pixels using various interpolation methods.
    """
    real_world_area_um = 36 * (10**6)  # Target pixel count
    current_total_pixels = image.shape[0] * image.shape[1]
    scale_factor = (real_world_area_um / current_total_pixels) ** 0.5
    new_dimensions = (int(image.shape[1] * scale_factor), int(image.shape[0] * scale_factor))
    
    if method == 'nearest':
        return cv2.resize(image, new_dimensions, interpolation=cv2.INTER_NEAREST)
    elif method == 'lanczos':
        return cv2.resize(image, new_dimensions, interpolation=cv2.INTER_LANCZOS4)
    elif method == 'inter_cubic':
        return cv2.resize(image, new_dimensions, interpolation=cv2.INTER_CUBIC)
    else:
        return cv2.resize(image, new_dimensions, interpolation=cv2.INTER_LINEAR)

def pixels_per_micrometer(img):
    """
    Calculate the number of pixels per micrometer.
    """
    real_world_area_um = 36 * (10**6)
    total_pixels = img.shape[0] * img.shape[1]
    return total_pixels / real_world_area_um

def process_image(image_array):
    """
    Process the image array to detect and classify particles based on their size and the given configuration.
    """
    if image_array is None:
        print("Error: No image data.")
        return
    
    gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

    opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    thresh = upscale_image(opening, 'inter_cubic')

    ppm = pixels_per_micrometer(thresh)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    diameters_pixels = [np.sqrt(4 * cv2.contourArea(contour) / np.pi) for contour in contours]
    diameters_um = [diameter_pixel / ppm for diameter_pixel in diameters_pixels]

    count_up_to_1um = sum(1 for d in diameters_um if d <= 1)
    count_up_to_2_5um = sum(1 for d in diameters_um if 1 < d <= 2.5)
    count_up_to_10um = sum(1 for d in diameters_um if 2.5 < d <= 10)
    count_above_10um = sum(1 for d in diameters_um if d > 10)

    # Returning results based on the attached image configuration
    results = {
        "<=1um": count_up_to_1um,
        "1-2.5um": count_up_to_2_5um,
        "2.5-10um": count_up_to_10um,
        ">10um": count_above_10um,
        "Total": count_up_to_1um + count_up_to_2_5um + count_up_to_10um + count_above_10um
    }
    
    # Define pollution levels based on dot count per cm^2 as shown in the attached image
    pollution_level = "Unknown"
    dots_per_cm2 = results[">10um"] / 36  # Assuming a square centimeter is 10x10 pixels

    if dots_per_cm2 > 50:
        pollution_level = "Very High"
    elif dots_per_cm2 >= 26:
        pollution_level = "High"
    elif dots_per_cm2 >= 11:
        pollution_level = "Medium"
    elif dots_per_cm2 < 11:
        pollution_level = "Low"
    
    return {
        "Pollution Level": pollution_level,
        "Details": results
    }

# The rest of the Streamlit interface would use this process_image function to display results.
