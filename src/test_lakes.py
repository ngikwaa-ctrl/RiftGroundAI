from lakes import LAKES

print("🌍 Rift Valley Lakes")

for lake, coords in LAKES.items():
    print(
        f"{lake}: "
        f"Latitude = {coords['lat']}, "
        f"Longitude = {coords['lon']}"
    )
