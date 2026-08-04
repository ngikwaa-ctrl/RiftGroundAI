import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

print("=" * 50)
print("🌍 RiftGroundAI")
print("=" * 50)

print(f"NumPy Version: {np.__version__}")
print(f"Pandas Version: {pd.__version__}")

# Sample data
lake_level = np.arange(1, 11)
groundwater_index = lake_level ** 2

df = pd.DataFrame({
    "Lake Level": lake_level,
    "Groundwater Index": groundwater_index
})

print("\nSample Data:")
print(df)

plt.plot(lake_level, groundwater_index, marker="o")
plt.title("Sample Groundwater vs Lake Level")
plt.xlabel("Lake Level")
plt.ylabel("Groundwater Index")
plt.grid(True)

plt.show()
