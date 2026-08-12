import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor

# Import project configuration
from config import LAKES, DATA_FOLDER

print("🤖 RiftGroundAI AI Forecast v2")
print("=" * 60)

# Data folder
data_folder = Path(DATA_FOLDER)

# Forecast each lake
for lake in LAKES.keys():

    print(f"\nForecasting {lake}...")

    try:

        # Load historical data
        file = data_folder / f"{lake}_monthly_ndwi.csv"

        if not file.exists():
            print(f"❌ Missing file: {file}")
            continue

        df = pd.read_csv(file)

        if df.empty:
            print("❌ No historical data found.")
            continue

        # Create date column
        df["Date"] = pd.to_datetime(
            df["Year"].astype(str)
            + "-"
            + df["Month"].astype(str)
            + "-01"
        )

        df = df.sort_values("Date").reset_index(drop=True)

        # Feature engineering
        df["Time"] = np.arange(len(df))
        df["MonthNum"] = df["Date"].dt.month

        X = df[["Time", "MonthNum"]]
        y = df["Average_NDWI"]

        # Train Random Forest model
        model = RandomForestRegressor(
            n_estimators=300,
            random_state=42
        )

        model.fit(X, y)

        # Forecast until December 2027
        last_date = df.iloc[-1]["Date"]
        last_time = int(df.iloc[-1]["Time"])

        future_rows = []
        future_date = last_date

        while future_date < pd.Timestamp("2027-12-01"):

            future_date += pd.DateOffset(months=1)
            last_time += 1

            future_features = pd.DataFrame({
                "Time": [last_time],
                "MonthNum": [future_date.month]
            })

            prediction = model.predict(future_features)[0]

            future_rows.append({
                "Year": future_date.year,
                "Month": future_date.month,
                "Predicted_NDWI": round(float(prediction), 4)
            })

        forecast_df = pd.DataFrame(future_rows)

        outfile = data_folder / f"{lake}_forecast.csv"

        forecast_df.to_csv(outfile, index=False)

        print(f"✅ Saved {outfile}")
        print(forecast_df.head())

    except Exception as e:
        print(f"❌ Error forecasting {lake}: {e}")

print("\n🎉 AI Forecasting Complete!")
