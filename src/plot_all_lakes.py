import pandas as pd
import matplotlib.pyplot as plt

# Read the data
df = pd.read_csv("data/all_lakes_2024.csv")

# Sort from highest to lowest NDWI
df = df.sort_values("Average NDWI", ascending=False)

plt.figure(figsize=(10, 6))

plt.bar(df["Lake"], df["Average NDWI"])

plt.title("Average NDWI of Kenyan Rift Valley Lakes (2024)")
plt.xlabel("Lake")
plt.ylabel("Average NDWI")

plt.axhline(0, linestyle="--")

plt.tight_layout()
plt.show()
