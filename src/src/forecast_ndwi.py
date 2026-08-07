import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor

print("🤖 RiftGroundAI AI Forecast v2")
print("=" * 60)

data_folder = Path("data")

lakes = [
    "Baringo",
    "Bogoria",
    "Nakuru",
    "Elementaita",
    "Naivasha",
    "Turkana",
    "Magadi"
]

for lake in lakes:

    print(f"\nForecasting {lake}...")

    file = data_folder / f"{lake}_monthly_ndwi.csv"

    df = pd.read_csv(file)

    # -----------------------------
    # Build a date column
    # -----------------------------
    df["Date"] = pd.to_datetime(
        df["Year"].astype(str) + "-" +
        df["Month"].astype(str) + "-01"
    )

    df = df.sort_values("Date").reset_index(drop=True)

    # -----------------------------
    # Create features
    # -----------------------------
    df["Time"] = np.arange(len(df))
    df["MonthNum"] = df["Date"].dt.month

    X = df[["Time", "MonthNum"]]
    y = df["Average_NDWI"]

    # -----------------------------
    # Train AI model
    # -----------------------------
    model = RandomForestRegressor(
        n_estimators=300,
        random_state=42
    )

    model.fit(X, y)

    # -----------------------------
    # Forecast until Dec 2027
    # -----------------------------
    last_date = df.iloc[-1]["Date"]
    last_time = int(df.iloc[-1]["Time"])

    forecast = []

    future_date = last_date

    while future_date < pd.Timestamp("2027-12-01"):

        future_date = future_date + pd.DateOffset(months=1)
        last_time += 1

        features = pd.DataFrame({
            "Time": [last_time],
            "MonthNum": [future_date.month]
        })

        prediction = model.predict(features)[0]

        forecast.append({
            "Year": future_date.year,
            "Month": future_date.month,
            "Predicted_NDWI": round(float(prediction), 4)
        })

    forecast_df = pd.DataFrame(forecast)

    outfile = data_folder / f"{lake}_forecast.csv"

    forecast_df.to_csv(outfile, index=False)

    print(f"Saved {outfile}")
    print(forecast_df.head())

print("\n🎉 AI Forecasting Complete!")
