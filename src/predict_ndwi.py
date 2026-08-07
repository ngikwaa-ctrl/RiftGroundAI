import pandas as pd
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import numpy as np

# Load the monthly NDWI data
df = pd.read_csv("data/monthly_ndwi.csv")

# Create a time index
df = df.sort_values(["Year", "Month"]).reset_index(drop=True)
df["Time"] = np.arange(len(df))

# Prepare data for the model
X = df[["Time"]]
y = df["Average_NDWI"]

# Train the AI model
model = LinearRegression()
model.fit(X, y)

# Predict historical values
df["Prediction"] = model.predict(X)

# Predict the next 12 months
future_time = np.arange(len(df), len(df) + 12).reshape(-1, 1)
future_predictions = model.predict(future_time)

print("📈 Predicted NDWI for the next 12 months:\n")

for i, value in enumerate(future_predictions, start=1):
    print(f"Month {i}: {value:.4f}")

# Plot results
plt.figure(figsize=(12, 6))

plt.plot(
    df["Time"],
    df["Average_NDWI"],
    marker="o",
    label="Observed NDWI"
)

plt.plot(
    df["Time"],
    df["Prediction"],
    color="red",
    linewidth=2,
    label="AI Trend"
)

plt.xlabel("Time (Months)")
plt.ylabel("Average NDWI")
plt.title("Lake Baringo NDWI Trend (2020–2024)")
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()
