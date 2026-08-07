import pandas as pd
import matplotlib.pyplot as plt

print("Starting...")

df = pd.read_csv("data/monthly_ndwi.csv")
print("CSV loaded!")

df["Date"] = pd.to_datetime(
    df["Year"].astype(str) + "-" + df["Month"].astype(str)
)

print("Creating graph...")

plt.figure(figsize=(12, 6))
plt.plot(df["Date"], df["Average_NDWI"], marker="o")
plt.grid(True)

print("Showing graph...")
plt.show()

print("Finished!")
