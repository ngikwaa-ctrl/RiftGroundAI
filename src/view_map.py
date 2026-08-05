import ee
import geemap

# Initialize Earth Engine
ee.Initialize(project="riftgroundai")

# Study area (Lake Naivasha)
lake = ee.Geometry.Point([36.36, -0.77]).buffer(15000)

# Get a cloud-free Sentinel-2 image
image = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(lake)
    .filterDate("2024-01-01", "2024-12-31")
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    .median()
)

# Visualization settings
vis_params = {
    "bands": ["B4", "B3", "B2"],
    "min": 0,
    "max": 3000
}

# Create map
Map = geemap.Map(center=[-0.77, 36.36], zoom=11)

Map.addLayer(image, vis_params, "Sentinel-2")
Map.addLayer(lake, {"color": "red"}, "Study Area")

Map
