import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv

# Get the base directory of the project
BASE_DIR = Path(__file__).parent.absolute()

# API Keys - Load from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# Model Configuration - Updated for local deployment
MODEL_PATH = BASE_DIR / "attached_assets" / "efficientnet_greenlens.pth"
MODEL_INPUT_SIZE = 224
NUM_CLASSES = 22

# Disease Categories - Matching model exactly
DISEASE_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___healthy"
]

# Weather suitability rules for diseases
WEATHER_DISEASE_RULES = {
    "Apple___Apple_scab": {"favorable_temp": (15, 25), "favorable_humidity": (60, 100), "rain_risk": True},
    "Apple___Black_rot": {"favorable_temp": (20, 30), "favorable_humidity": (70, 100), "rain_risk": True},
    "Apple___Cedar_apple_rust": {"favorable_temp": (15, 25), "favorable_humidity": (80, 100), "rain_risk": True},
    "Corn_(maize)___Cercospora_leaf_spot_Gray_leaf_spot": {"favorable_temp": (22, 32), "favorable_humidity": (60, 100), "rain_risk": True},
    "Corn_(maize)___Common_rust_": {"favorable_temp": (16, 25), "favorable_humidity": (95, 100), "rain_risk": True},
    "Corn_(maize)___Northern_Leaf_Blight": {"favorable_temp": (18, 27), "favorable_humidity": (90, 100), "rain_risk": True},
    "Grape___Black_rot": {"favorable_temp": (20, 30), "favorable_humidity": (70, 100), "rain_risk": True},
    "Grape___Esca_(Black_Measles)": {"favorable_temp": (25, 35), "favorable_humidity": (50, 80), "rain_risk": False},
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {"favorable_temp": (20, 30), "favorable_humidity": (80, 100), "rain_risk": True},
    "Orange___Haunglongbing_(Citrus_greening)": {"favorable_temp": (25, 35), "favorable_humidity": (60, 90), "rain_risk": False},
    "Peach___Bacterial_spot": {"favorable_temp": (24, 30), "favorable_humidity": (80, 100), "rain_risk": True},
    "Pepper,_bell___Bacterial_spot": {"favorable_temp": (25, 35), "favorable_humidity": (80, 100), "rain_risk": True},
    "Potato___Early_blight": {"favorable_temp": (24, 29), "favorable_humidity": (90, 100), "rain_risk": True},
    "Potato___Late_blight": {"favorable_temp": (15, 20), "favorable_humidity": (90, 100), "rain_risk": True},
    "Tomato___Bacterial_spot": {"favorable_temp": (24, 30), "favorable_humidity": (80, 100), "rain_risk": True},
}



UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
STATIC_DIR = BASE_DIR / "static"

# Server
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", 5000))
DEBUG = os.getenv("DEBUG", "True") == "True"

# Ensure directories
for d in (UPLOAD_DIR, OUTPUT_DIR, STATIC_DIR, STATIC_DIR / "outputs"):
    d.mkdir(exist_ok=True)
