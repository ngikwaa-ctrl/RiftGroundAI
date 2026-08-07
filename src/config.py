"""
RiftGroundAI Configuration File
-------------------------------
Store all reusable project settings here.
"""

# Google Earth Engine Project
PROJECT_NAME = "riftgroundai"

# Analysis period
START_YEAR = 2020
END_YEAR = 2026

# Lakes (Longitude, Latitude)
LAKES = {
    "Baringo": [36.08, 0.63],
    "Bogoria": [36.10, 0.26],
    "Nakuru": [36.08, -0.30],
    "Elementaita": [36.27, -0.46],
    "Naivasha": [36.37, -0.77],
    "Turkana": [36.10, 3.50],
    "Magadi": [36.28, -1.90]
}

# Sentinel-2 Settings
DATASET = "COPERNICUS/S2_SR_HARMONIZED"
MAX_CLOUD = 10

# NDWI Bands
GREEN_BAND = "B3"
NIR_BAND = "B8"

# Buffer size around each lake (metres)
BUFFER_SIZE = 5000

# Output folder
DATA_FOLDER = "data"
