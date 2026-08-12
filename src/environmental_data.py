import ee
import pandas as pd
from pathlib import Path
from datetime import datetime


# ============================================================
# RiftGroundAI Environmental Data Collection
# NDVI + Rainfall
# ============================================================

print("🌍 RiftGroundAI - Environmental Data Collection")
print("=" * 60)


# ============================================================
# INITIALIZE GOOGLE EARTH ENGINE
# ============================================================

ee.Initialize(project="riftgroundai")

print("✅ Google Earth Engine initialized")


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_FOLDER = Path(__file__).resolve().parent.parent
DATA_FOLDER = PROJECT_FOLDER / "data"

DATA_FOLDER.mkdir(
    exist_ok=True
)


# ============================================================
# DATE RANGE
# ============================================================

current_year = datetime.now().year
current_month = datetime.now().month

print(
    f"Collecting environmental data from 2020 "
    f"to {current_year}-{current_month:02d}"
)


# ============================================================
# RIFT VALLEY LAKES
# ============================================================

lakes = {

    "Baringo": [36.08, 0.63],

    "Bogoria": [36.10, 0.26],

    "Nakuru": [36.08, -0.30],

    "Elementaita": [36.27, -0.46],

    "Naivasha": [36.37, -0.77],

    "Turkana": [36.10, 3.50],

    "Magadi": [36.28, -1.90]
}


# ============================================================
# PROCESS EACH LAKE
# ============================================================

for lake_name, coords in lakes.items():

    print("\n" + "=" * 60)

    print(
        f"🌊 Processing {lake_name}"
    )

    print("=" * 60)

    point = ee.Geometry.Point(coords)

    region = point.buffer(5000)

    monthly_results = []

    # ========================================================
    # YEAR LOOP
    # ========================================================

    for year in range(
        2020,
        current_year + 1
    ):

        # ====================================================
        # MONTH LOOP
        # ====================================================

        for month in range(1, 13):

            # Don't request future months

            if (
                year == current_year
                and month > current_month
            ):
                break

            # =================================================
            # DATE RANGE
            # =================================================

            start = ee.Date.fromYMD(
                year,
                month,
                1
            )

            if month == 12:

                end = ee.Date.fromYMD(
                    year + 1,
                    1,
                    1
                )

            else:

                end = ee.Date.fromYMD(
                    year,
                    month + 1,
                    1
                )

            # =================================================
            # NDVI — SENTINEL-2
            # =================================================

            sentinel = (

                ee.ImageCollection(
                    "COPERNICUS/S2_SR_HARMONIZED"
                )

                .filterBounds(region)

                .filterDate(
                    start,
                    end
                )

                .filter(
                    ee.Filter.lt(
                        "CLOUDY_PIXEL_PERCENTAGE",
                        20
                    )
                )
            )

            sentinel_count = (
                sentinel.size().getInfo()
            )

            # =================================================
            # NDVI CALCULATION
            # =================================================

            ndvi_value = None

            if sentinel_count > 0:

                image = sentinel.mean()

                ndvi = image.normalizedDifference(
                    [
                        "B8",
                        "B4"
                    ]
                )

                ndvi_stats = ndvi.reduceRegion(

                    reducer=ee.Reducer.mean(),

                    geometry=region,

                    scale=10,

                    maxPixels=1e9
                )

                ndvi_result = (
                    ndvi_stats
                    .get("nd")
                    .getInfo()
                )

                if ndvi_result is not None:

                    ndvi_value = float(
                        ndvi_result
                    )

            # =================================================
            # RAINFALL — CHIRPS
            # =================================================

            chirps = (

                ee.ImageCollection(
                    "UCSB-CHG/CHIRPS/DAILY"
                )

                .filterBounds(region)

                .filterDate(
                    start,
                    end
                )
            )

            rainfall_value = None

            if chirps.size().getInfo() > 0:

                rainfall_image = (
                    chirps
                    .sum()
                )

                rainfall_stats = (
                    rainfall_image
                    .reduceRegion(

                        reducer=ee.Reducer.mean(),

                        geometry=region,

                        scale=5000,

                        maxPixels=1e9
                    )
                )

                rainfall_result = (
                    rainfall_stats
                    .get("precipitation")
                    .getInfo()
                )

                if rainfall_result is not None:

                    rainfall_value = float(
                        rainfall_result
                    )

            # =================================================
            # SAVE RESULT
            # =================================================

            if (
                ndvi_value is not None
                or rainfall_value is not None
            ):

                monthly_results.append(

                    {
                        "Year": year,

                        "Month": month,

                        "NDVI": ndvi_value,

                        "Rainfall_mm": rainfall_value
                    }
                )

                print(

                    f"{year}-{month:02d} | "

                    f"NDVI: "
                    f"{ndvi_value:.4f}"
                    if ndvi_value is not None
                    else
                    f"{year}-{month:02d} | "
                    f"NDVI: N/A",

                    end=" | "
                )

                print(

                    f"Rainfall: "
                    f"{rainfall_value:.2f} mm"
                    if rainfall_value is not None
                    else
                    "Rainfall: N/A"
                )

    # ========================================================
    # CREATE DATAFRAME
    # ========================================================

    df = pd.DataFrame(
        monthly_results
    )

    # ========================================================
    # SAVE CSV
    # ========================================================

    output_file = (
        DATA_FOLDER /
        f"{lake_name}_environmental.csv"
    )

    df.to_csv(
        output_file,
        index=False
    )

    print()

    print(
        f"✅ Saved: {output_file}"
    )

    print(
        f"📊 Records: {len(df)}"
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)

print(
    "🎉 ENVIRONMENTAL DATA COLLECTION COMPLETE!"
)

print("=" * 60)

print(
    "NDVI + Rainfall data is now available "
    "for the RiftGroundAI dashboard."
)
