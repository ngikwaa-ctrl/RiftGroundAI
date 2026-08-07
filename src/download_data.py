import ee
import pandas as pd

# Initialize Earth Engine
ee.Initialize(project="riftgroundai")

print("✅ Earth Engine initialized!")

# Lake Baringo
lake = ee.Geometry.Point([36.08, 0.63])

results = []

for year in range(2020, 2026):

    for month in range(1, 13):

        start = ee.Date.fromYMD(year, month, 1)

        if month == 12:
            end = ee.Date.fromYMD(year + 1, 1, 1)
        else:
            end = ee.Date.fromYMD(year, month + 1, 1)

        collection = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(lake)
            .filterDate(start, end)
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 10))
        )

        count = collection.size().getInfo()

        if count == 0:
            continue

        image = collection.mean()

        ndwi = image.normalizedDifference(["B3", "B8"])

        stats = ndwi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=lake.buffer(5000),
            scale=10,
            maxPixels=1e9,
        )

        value = stats.get("nd")

        if value is None:
            continue

        ndwi_value = value.getInfo()

        print(f"{year}-{month:02d} | Images: {count} | NDWI: {ndwi_value:.4f}")

        results.append({
            "Year": year,
            "Month": month,
            "Images": count,
            "Average_NDWI": ndwi_value
        })

df = pd.DataFrame(results)

df.to_csv("data/monthly_ndwi.csv", index=False)

print("\n✅ Finished!")
print(df.head())
