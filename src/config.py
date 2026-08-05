"""
Configuration file for RiftGroundAI
"""

from pathlib import Path

# -----------------------------
# Project Directories
# -----------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUT_DIR = PROJECT_ROOT / "outputs"
FIGURE_DIR = PROJECT_ROOT / "figures"

# Create directories automatically
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FIGURE_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Study Area
# -----------------------------

LAKES = [
    "Lake Naivasha",
    "Lake Nakuru",
    "Lake Bogoria",
    "Lake Baringo",
    "Lake Elementaita"
]

# -----------------------------
# Time Range
# -----------------------------

START_DATE = "2015-01-01"
END_DATE = "2025-12-31"

# -----------------------------
# Satellite
# -----------------------------

SATELLITE = "COPERNICUS/S2_SR_HARMONIZED"

# -----------------------------
# Water Detection
# -----------------------------

NDWI_THRESHOLD = 0.2

print("Configuration loaded successfully.")
