import ee
import pandas as pd
from datetime import datetime

# Import project configuration
from config import (
    PROJECT_NAME,
    LAKES,
    DATASET,
    MAX_CLOUD,
    GREEN_BAND,
    NIR_BAND,
    BUFFER_SIZE,
    DATA_FOLDER,
    START_YEAR,
)

# -------------------------------
# Initialize Earth Engine
# -------------------------------
ee.Initialize(project=PROJECT_NAME)

print("🌍 RiftGroundAI - Multi-Lake Monthly Analysis")
print("=" * 60)

# -------------------------------
# Current date
# -------------------------------
current_year = datetime.now().year
current_month = datetime.now().month

print(
    f"Collecting data from {START_YEAR} to {current_year}-{current_month:02d}")

# -------------------------------
# Process every lake
# -------------------------------
for lake_name, coords in LAKES.items():

    print("\n" + "=" * 60)
    print(f"Analyzing {lake_name}")
    print("=" * 60)

    point = ee.Geometry.Point(coords)

    monthly_results = []

    try:

        # Loop through all years
        for year in range(START_YEAR, current_year + 1):

            # Loop through months
            for month in range(1, 13):

                # Don't request future months
                if year == current_year and month > current_month:
                    break

                start = ee.Date.fromYMD(year, month, 1)

                if month == 12:
                    end = ee.Date.fromYMD(year + 1, 1, 1)
                else:
                    end = ee.Date.fromYMD(year, month + 1, 1)

                # Load Sentinel-2 imagery
                collection = (
                    ee.ImageCollection(DATASET)
                    .filterBounds(point)
                    .filterDate(start, end)
                    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", MAX_CLOUD))
                )

                count = collection.size().getInfo()

                if count == 0:
                    continue

                # Create monthly composite
                image = collection.mean()

                # Calculate NDWI
                ndwi = image.normalizedDifference(
                    [GREEN_BAND, NIR_BAND]
                )

                # Calculate average NDWI around the lake
                stats = ndwi.reduceRegion(
                    reducer=ee.Reducer.mean(),
                    geometry=point.buffer(BUFFER_SIZE),
                    scale=10,
                    maxPixels=1e9,
                )

                value = stats.get("nd")

                if value is None:
                    continue

                ndwi_value = value.getInfo()

                print(
                    f"{year}-{month:02d} | "
                    f"Images: {count} | "
                    f"NDWI: {ndwi_value:.4f}"
                )

                monthly_results.append(
                    {
                        "Year": year,
                        "Month": month,
                        "Images": count,
                        "Average_NDWI": ndwi_value,
                    }
                )

        df = pd.DataFrame(monthly_results)

        filename = f"{DATA_FOLDER}/{lake_name}_monthly_ndwi.csv"

        df.to_csv(filename, index=False)

        print(f"\n✅ Saved {filename}")
        print(df.tail())

    except Exception as e:
        print(f"❌ Error processing {lake_name}: {e}")

print("\n🎉 ALL LAKES FINISHED!")
