import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# -------------------------
# Page Setup
# -------------------------
st.set_page_config(
    page_title="RiftGroundAI",
    page_icon="🌍",
    layout="wide"
)

st.title("🌍 RiftGroundAI")
st.subheader("AI-Powered Rift Valley Lake Monitoring & Forecasting")

# -------------------------
# Lakes
# -------------------------
lakes = [
    "Baringo",
    "Bogoria",
    "Nakuru",
    "Elementaita",
    "Naivasha",
    "Turkana",
    "Magadi"
]

# -------------------------
# Sidebar
# -------------------------
st.sidebar.title("Controls")

selected_lake = st.sidebar.selectbox(
    "Choose a Lake",
    lakes
)

# -------------------------
# Load Historical Data
# -------------------------
historical_file = Path(f"data/{selected_lake}_monthly_ndwi.csv")

forecast_file = Path(f"data/{selected_lake}_forecast.csv")

historical = pd.read_csv(historical_file)

forecast = pd.read_csv(forecast_file)

# -------------------------
# Create Date Columns
# -------------------------
historical["Date"] = pd.to_datetime(
    historical["Year"].astype(str) + "-" +
    historical["Month"].astype(str) + "-01"
)

forecast["Date"] = pd.to_datetime(
    forecast["Year"].astype(str) + "-" +
    forecast["Month"].astype(str) + "-01"
)

# -------------------------
# Plot
# -------------------------
fig, ax = plt.subplots(figsize=(14, 6))

ax.plot(
    historical["Date"],
    historical["Average_NDWI"],
    linewidth=2,
    marker="o",
    label="Historical"
)

ax.plot(
    forecast["Date"],
    forecast["Predicted_NDWI"],
    linestyle="--",
    linewidth=2,
    marker="x",
    label="AI Forecast"
)

ax.set_title(selected_lake)

ax.set_ylabel("Average NDWI")

ax.grid(True)

ax.legend()

st.pyplot(fig)

# -------------------------
# Metrics
# -------------------------
latest = historical.iloc[-1]["Average_NDWI"]

forecast_latest = forecast.iloc[-1]["Predicted_NDWI"]

col1, col2 = st.columns(2)

with col1:

    st.metric(
        "Latest Observed NDWI",
        round(latest, 3)
    )

with col2:

    st.metric(
        "Forecast NDWI (Dec 2027)",
        round(forecast_latest, 3)
    )

# -------------------------
# AI Risk Assessment
# -------------------------
st.markdown("---")

st.header("🤖 AI Assessment")

if forecast_latest > 0.45:

    st.success(
        "🟢 High water availability predicted through 2027."
    )

elif forecast_latest > 0.25:

    st.warning(
        "🟡 Moderate water levels predicted."
    )

else:

    st.error(
        "🔴 Low water levels predicted. Continued monitoring is recommended."
    )

# -------------------------
# Tables
# -------------------------
st.markdown("---")

st.subheader("Historical Data")

st.dataframe(historical)

st.subheader("Forecast Data")

st.dataframe(forecast)
