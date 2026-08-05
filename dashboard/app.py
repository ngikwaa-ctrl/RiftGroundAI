import streamlit as st
import ee
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")

st.title("🌍 RiftGroundAI")
st.subheader("NDWI Water Detection")

# Initialize Earth Engine
ee.Initialize(project="riftgroundai")

# Lake Naivasha
lake = ee.Geometry.Point([36.36, -0.77])

# Sentinel-2 image
image = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(lake)
    .filterDate("2024-01-01", "2024-12-31")
    .sort("CLOUDY_PIXEL_PERCENTAGE")
    .first()
)

# Calculate NDWI
ndwi = image.normalizedDifference(["B3", "B8"]).rename("NDWI")

# Visualization
vis = {
    "min": -1,
    "max": 1,
    "palette": [
        "brown",
        "yellow",
        "green",
        "cyan",
        "blue"
    ]
}

# Create map
m = folium.Map(
    location=[-0.77, 36.36],
    zoom_start=11
)

# Add NDWI layer
map_id = ndwi.getMapId(vis)

folium.TileLayer(
    tiles=map_id["tile_fetcher"].url_format,
    attr="Google Earth Engine",
    name="NDWI"
).add_to(m)

folium.LayerControl().add_to(m)

st_folium(m, width=1200, height=700)
