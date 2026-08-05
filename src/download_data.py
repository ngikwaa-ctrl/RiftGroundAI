"""
Download Sentinel-2 data from Google Earth Engine.
"""

import ee

# Initialize Earth Engine
ee.Initialize(project="riftgroundai")

print("✅ Earth Engine initialized!")

# --------------------------------------
# Study Area: Lake Naivasha
# --------------------------------------

lake_naivasha = ee.Geometry.Point([36.36, -0.77]).buffer(15000)

# --------------------------------------
# Sentinel-2 Image Collection
# --------------------------------------

images = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(lake_naivasha)
    .filterDate("2024-01-01", "2024-12-31")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
)

print("Images found:", images.size().getInfo())
