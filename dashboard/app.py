import streamlit as st
import pandas as pd
import folium
import numpy as np

from pathlib import Path
from streamlit_folium import st_folium


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="RiftGroundAI",
    page_icon="🌍",
    layout="wide"
)


# ============================================================
# PATHS
# ============================================================

DASHBOARD_FOLDER = Path(__file__).parent
PROJECT_FOLDER = DASHBOARD_FOLDER.parent

DATA_LOCATIONS = [
    DASHBOARD_FOLDER / "data",
    PROJECT_FOLDER / "data"
]


def find_data_file(filename):

    for folder in DATA_LOCATIONS:

        file_path = folder / filename

        if file_path.exists():
            return file_path

    return None


# ============================================================
# LAKE LOCATIONS
# ============================================================

LAKES = {

    "Turkana": {
        "lat": 3.50,
        "lon": 36.10
    },

    "Baringo": {
        "lat": 0.63,
        "lon": 36.08
    },

    "Bogoria": {
        "lat": 0.25,
        "lon": 36.10
    },

    "Nakuru": {
        "lat": -0.30,
        "lon": 36.08
    },

    "Elementaita": {
        "lat": -0.46,
        "lon": 36.27
    },

    "Naivasha": {
        "lat": -0.77,
        "lon": 36.37
    },

    "Magadi": {
        "lat": -1.90,
        "lon": 36.28
    }

}


# ============================================================
# RISK LEVEL
# ============================================================

def get_risk_level(score):

    if score >= 70:
        return "HIGH"

    elif score >= 40:
        return "MODERATE"

    return "LOW"


# ============================================================
# RISK COLOR
# ============================================================

def get_risk_color(score):

    if score >= 70:
        return "red"

    elif score >= 40:
        return "orange"

    return "green"


# ============================================================
# LAKE INFORMATION + RISK CALCULATION
# ============================================================

def get_lake_information(lake):

    history_file = find_data_file(
        f"{lake}_monthly_ndwi.csv"
    )

    forecast_file = find_data_file(
        f"{lake}_forecast.csv"
    )

    environmental_file = find_data_file(
        f"{lake}_environmental.csv"
    )

    latest_ndwi = None
    forecast_ndwi = None
    latest_ndvi = None
    latest_rainfall = None

    change = 0

    # ========================================================
    # HISTORICAL NDWI
    # ========================================================

    if history_file is not None:

        try:

            history = pd.read_csv(history_file)

            if "Average_NDWI" in history.columns:

                history["Average_NDWI"] = pd.to_numeric(
                    history["Average_NDWI"],
                    errors="coerce"
                )

                history = history.dropna(
                    subset=["Average_NDWI"]
                )

                if not history.empty:

                    latest_ndwi = float(
                        history.iloc[-1]["Average_NDWI"]
                    )

        except Exception:
            pass

    # ========================================================
    # AI FORECAST
    # ========================================================

    if forecast_file is not None:

        try:

            forecast = pd.read_csv(
                forecast_file
            )

            if "Predicted_NDWI" in forecast.columns:

                forecast["Predicted_NDWI"] = pd.to_numeric(
                    forecast["Predicted_NDWI"],
                    errors="coerce"
                )

                forecast = forecast.dropna(
                    subset=["Predicted_NDWI"]
                )

                if not forecast.empty:

                    # Use the final forecast value
                    forecast_ndwi = float(
                        forecast.iloc[-1]["Predicted_NDWI"]
                    )

        except Exception:
            pass

    # ========================================================
    # ENVIRONMENTAL DATA
    # ========================================================

    if environmental_file is not None:

        try:

            environmental = pd.read_csv(
                environmental_file
            )

            if not environmental.empty:

                # ------------------------------------------------
                # SORT ENVIRONMENTAL DATA
                # ------------------------------------------------

                if (
                    "Year" in environmental.columns
                    and "Month" in environmental.columns
                ):

                    environmental["Year"] = pd.to_numeric(
                        environmental["Year"],
                        errors="coerce"
                    )

                    environmental["Month"] = pd.to_numeric(
                        environmental["Month"],
                        errors="coerce"
                    )

                    environmental["Date"] = pd.to_datetime(
                        dict(
                            year=environmental["Year"],
                            month=environmental["Month"],
                            day=1
                        ),
                        errors="coerce"
                    )

                    environmental = (
                        environmental
                        .sort_values("Date")
                    )

                # ------------------------------------------------
                # NDVI
                # ------------------------------------------------

                if "NDVI" in environmental.columns:

                    environmental["NDVI"] = pd.to_numeric(
                        environmental["NDVI"],
                        errors="coerce"
                    )

                    valid_ndvi = (
                        environmental["NDVI"]
                        .dropna()
                    )

                    if not valid_ndvi.empty:

                        latest_ndvi = float(
                            valid_ndvi.iloc[-1]
                        )

                # ------------------------------------------------
                # RAINFALL
                # ------------------------------------------------

                if "Rainfall_mm" in environmental.columns:

                    environmental["Rainfall_mm"] = pd.to_numeric(
                        environmental["Rainfall_mm"],
                        errors="coerce"
                    )

                    valid_rainfall = (
                        environmental["Rainfall_mm"]
                        .dropna()
                    )

                    if not valid_rainfall.empty:

                        latest_rainfall = float(
                            valid_rainfall.iloc[-1]
                        )

        except Exception:
            pass

    # ========================================================
    # PROJECTED WATER CHANGE
    # ========================================================

    if (
        latest_ndwi is not None
        and forecast_ndwi is not None
    ):

        change = (
            forecast_ndwi
            - latest_ndwi
        )

    else:

        change = 0

    # ========================================================
    # WATER STRESS
    #
    # IMPORTANT:
    # This measures projected deterioration.
    #
    # It does NOT mean:
    # "40/50 = lake water is currently low."
    #
    # It means:
    # "40/50 = large projected decline."
    # ========================================================

    if change <= -0.15:

        water_score = 50

    elif change <= -0.10:

        water_score = 40

    elif change <= -0.05:

        water_score = 30

    elif change <= -0.03:

        water_score = 20

    elif change < 0:

        water_score = 10

    else:

        water_score = 0

    # ========================================================
    # VEGETATION STRESS
    # ========================================================

    if latest_ndvi is None:

        vegetation_score = 12

    elif latest_ndvi < 0.10:

        vegetation_score = 25

    elif latest_ndvi < 0.20:

        vegetation_score = 20

    elif latest_ndvi < 0.30:

        vegetation_score = 15

    elif latest_ndvi < 0.50:

        vegetation_score = 8

    else:

        vegetation_score = 0

    # ========================================================
    # RAINFALL STRESS
    # ========================================================

    if latest_rainfall is None:

        rainfall_score = 12

    elif latest_rainfall < 20:

        rainfall_score = 25

    elif latest_rainfall < 50:

        rainfall_score = 18

    elif latest_rainfall < 100:

        rainfall_score = 8

    else:

        rainfall_score = 0

    # ========================================================
    # TOTAL RISK SCORE
    # ========================================================

    risk_score = (
        water_score
        + vegetation_score
        + rainfall_score
    )

    risk_score = min(
        100,
        max(
            0,
            int(risk_score)
        )
    )

    # ========================================================
    # RISK LEVEL
    # ========================================================

    risk_level = get_risk_level(
        risk_score
    )

    return {

        "latest_ndwi": latest_ndwi,

        "forecast_ndwi": forecast_ndwi,

        "latest_ndvi": latest_ndvi,

        "latest_rainfall": latest_rainfall,

        "change": change,

        "water_score": water_score,

        "vegetation_score": vegetation_score,

        "rainfall_score": rainfall_score,

        "risk_score": risk_score,

        "risk_level": risk_level

    }


# ============================================================
# LOAD SELECTED LAKE DATA
# ============================================================

def load_lake_data(lake):

    history_file = find_data_file(
        f"{lake}_monthly_ndwi.csv"
    )

    forecast_file = find_data_file(
        f"{lake}_forecast.csv"
    )

    environmental_file = find_data_file(
        f"{lake}_environmental.csv"
    )

    history = pd.DataFrame()
    forecast = pd.DataFrame()
    environmental = pd.DataFrame()

    # HISTORY

    if history_file is not None:

        try:
            history = pd.read_csv(
                history_file
            )

        except Exception:
            history = pd.DataFrame()

    # FORECAST

    if forecast_file is not None:

        try:
            forecast = pd.read_csv(
                forecast_file
            )

        except Exception:
            forecast = pd.DataFrame()

    # ENVIRONMENTAL

    if environmental_file is not None:

        try:
            environmental = pd.read_csv(
                environmental_file
            )

        except Exception:
            environmental = pd.DataFrame()

    return (
        history,
        forecast,
        environmental
    )


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title(
    "🌍 RiftGroundAI"
)

st.sidebar.write(
    "AI-powered Rift Valley environmental monitoring."
)

lake = st.sidebar.selectbox(
    "Select Lake",
    list(LAKES.keys())
)

st.sidebar.divider()

st.sidebar.subheader(
    "Monitoring Layers"
)

st.sidebar.write("💧 NDWI — Water")
st.sidebar.write("🌱 NDVI — Vegetation")
st.sidebar.write("🌧️ Rainfall")
st.sidebar.write("🤖 AI Forecast")
st.sidebar.write("🚨 Risk Score")
st.sidebar.write("🎯 Decision Support")


# ============================================================
# LOAD DATA
# ============================================================

history, forecast, environmental = (
    load_lake_data(lake)
)

info = get_lake_information(
    lake
)

latest_ndwi = info["latest_ndwi"]
forecast_ndwi = info["forecast_ndwi"]
change = info["change"]

latest_ndvi = info["latest_ndvi"]
latest_rainfall = info["latest_rainfall"]

water_score = info["water_score"]
vegetation_score = info["vegetation_score"]
rainfall_score = info["rainfall_score"]

risk_score = info["risk_score"]
risk_level = info["risk_level"]

risk_color = get_risk_color(
    risk_score
)


# ============================================================
# HEADER
# ============================================================

st.title(
    "🌍 RiftGroundAI"
)

st.caption(
    "AI-powered Rift Valley Lake Monitoring & Forecasting"
)

st.divider()


# ============================================================
# AI INSIGHT
# ============================================================

st.subheader(
    "🤖 AI Insight"
)

if change < -0.03:

    st.warning(
        "The AI predicts a decline in lake water "
        "conditions by the end of the forecast period."
    )

elif change > 0.03:

    st.success(
        "The AI predicts an improvement in lake water "
        "conditions by the end of the forecast period."
    )

else:

    st.info(
        "The AI predicts relatively stable lake water "
        "conditions over the forecast period."
    )


# ============================================================
# LAKE OVERVIEW
# ============================================================

st.subheader(
    "📊 Lake Overview"
)

c1, c2, c3, c4 = st.columns(4)


with c1:

    st.metric(
        "Selected Lake",
        lake
    )


with c2:

    if latest_ndwi is not None:

        st.metric(
            "Latest NDWI",
            f"{latest_ndwi:.3f}"
        )

    else:

        st.metric(
            "Latest NDWI",
            "N/A"
        )


with c3:

    if forecast_ndwi is not None:

        st.metric(
            "AI Forecast NDWI",
            f"{forecast_ndwi:.3f}"
        )

    else:

        st.metric(
            "AI Forecast NDWI",
            "N/A"
        )


with c4:

    st.metric(
        "Projected Change",
        f"{change:+.3f}"
    )


# ============================================================
# ENVIRONMENTAL INTELLIGENCE
# ============================================================

st.subheader(
    "🌱 Environmental Intelligence"
)

st.caption(
    "RiftGroundAI combines water, vegetation and rainfall "
    "indicators to provide environmental context."
)

average_ndvi = None
average_rainfall = None

ndvi_trend = None
rainfall_trend = None


if not environmental.empty:

    environmental_work = (
        environmental.copy()
    )

    # ========================================================
    # CONVERT VALUES
    # ========================================================

    if "NDVI" in environmental_work.columns:

        environmental_work["NDVI"] = pd.to_numeric(
            environmental_work["NDVI"],
            errors="coerce"
        )

    if "Rainfall_mm" in environmental_work.columns:

        environmental_work["Rainfall_mm"] = pd.to_numeric(
            environmental_work["Rainfall_mm"],
            errors="coerce"
        )

    # ========================================================
    # SORT BY DATE
    # ========================================================

    if (
        "Year" in environmental_work.columns
        and "Month" in environmental_work.columns
    ):

        environmental_work["Year"] = pd.to_numeric(
            environmental_work["Year"],
            errors="coerce"
        )

        environmental_work["Month"] = pd.to_numeric(
            environmental_work["Month"],
            errors="coerce"
        )

        environmental_work["Date"] = pd.to_datetime(
            dict(
                year=environmental_work["Year"],
                month=environmental_work["Month"],
                day=1
            ),
            errors="coerce"
        )

        environmental_work = (
            environmental_work
            .sort_values("Date")
        )

    # ========================================================
    # NDVI
    # ========================================================

    if "NDVI" in environmental_work.columns:

        valid_ndvi = (
            environmental_work["NDVI"]
            .dropna()
        )

        if not valid_ndvi.empty:

            average_ndvi = float(
                valid_ndvi.mean()
            )

            if len(valid_ndvi) >= 2:

                ndvi_trend = (
                    valid_ndvi.iloc[-1]
                    - valid_ndvi.iloc[-2]
                )

    # ========================================================
    # RAINFALL
    # ========================================================

    if "Rainfall_mm" in environmental_work.columns:

        valid_rainfall = (
            environmental_work["Rainfall_mm"]
            .dropna()
        )

        if not valid_rainfall.empty:

            average_rainfall = float(
                valid_rainfall.mean()
            )

            if len(valid_rainfall) >= 2:

                rainfall_trend = (
                    valid_rainfall.iloc[-1]
                    - valid_rainfall.iloc[-2]
                )


# ============================================================
# ENVIRONMENTAL METRICS
# ============================================================

e1, e2, e3, e4 = st.columns(4)


with e1:

    if latest_ndvi is not None:

        st.metric(
            "🌱 Latest NDVI",
            f"{latest_ndvi:.3f}",
            delta=(
                f"{ndvi_trend:+.3f}"
                if ndvi_trend is not None
                else None
            )
        )

    else:

        st.metric(
            "🌱 Latest NDVI",
            "N/A"
        )


with e2:

    if average_ndvi is not None:

        st.metric(
            "🌱 Average NDVI",
            f"{average_ndvi:.3f}"
        )

    else:

        st.metric(
            "🌱 Average NDVI",
            "N/A"
        )


with e3:

    if latest_rainfall is not None:

        st.metric(
            "🌧️ Latest Rainfall",
            f"{latest_rainfall:.1f} mm",
            delta=(
                f"{rainfall_trend:+.1f} mm"
                if rainfall_trend is not None
                else None
            )
        )

    else:

        st.metric(
            "🌧️ Latest Rainfall",
            "N/A"
        )


with e4:

    if average_rainfall is not None:

        st.metric(
            "🌧️ Average Rainfall",
            f"{average_rainfall:.1f} mm"
        )

    else:

        st.metric(
            "🌧️ Average Rainfall",
            "N/A"
        )


# ============================================================
# ENVIRONMENTAL INTERPRETATION
# ============================================================

st.markdown(
    "### 🧠 Environmental Interpretation"
)

interpretation = []


# WATER

if change <= -0.05:

    interpretation.append(
        "💧 **Water:** The AI forecast indicates "
        "a declining water condition."
    )

elif change >= 0.05:

    interpretation.append(
        "💧 **Water:** The AI forecast indicates "
        "an improving water condition."
    )

else:

    interpretation.append(
        "💧 **Water:** The forecast indicates "
        "relatively stable water conditions."
    )


# VEGETATION

if latest_ndvi is not None:

    if latest_ndvi < 0:

        interpretation.append(
            "🌱 **Vegetation:** The latest NDVI is below "
            "zero, indicating limited vegetation signal "
            "in the monitored area."
        )

    elif latest_ndvi < 0.2:

        interpretation.append(
            "🌱 **Vegetation:** NDVI indicates relatively "
            "low vegetation activity."
        )

    elif latest_ndvi < 0.5:

        interpretation.append(
            "🌱 **Vegetation:** NDVI indicates moderate "
            "vegetation activity."
        )

    else:

        interpretation.append(
            "🌱 **Vegetation:** NDVI indicates relatively "
            "strong vegetation activity."
        )

else:

    interpretation.append(
        "🌱 **Vegetation:** NDVI data is unavailable."
    )


# RAINFALL

if latest_rainfall is not None:

    if latest_rainfall < 20:

        interpretation.append(
            "🌧️ **Rainfall:** Recent rainfall is "
            "relatively low."
        )

    elif latest_rainfall < 100:

        interpretation.append(
            "🌧️ **Rainfall:** Recent rainfall is "
            "within a moderate range."
        )

    else:

        interpretation.append(
            "🌧️ **Rainfall:** Recent rainfall is "
            "relatively high."
        )

else:

    interpretation.append(
        "🌧️ **Rainfall:** Rainfall data is unavailable."
    )


for message in interpretation:

    st.write(message)


# ============================================================
# ENVIRONMENTAL TREND CHARTS
# ============================================================

if not environmental.empty:

    chart_environmental = (
        environmental.copy()
    )

    if (
        "Year" in chart_environmental.columns
        and "Month" in chart_environmental.columns
    ):

        chart_environmental["Date"] = pd.to_datetime(
            dict(
                year=pd.to_numeric(
                    chart_environmental["Year"],
                    errors="coerce"
                ),
                month=pd.to_numeric(
                    chart_environmental["Month"],
                    errors="coerce"
                ),
                day=1
            ),
            errors="coerce"
        )

        chart_environmental = (
            chart_environmental
            .sort_values("Date")
        )

        # NDVI CHART

        if "NDVI" in chart_environmental.columns:

            ndvi_chart = chart_environmental[
                [
                    "Date",
                    "NDVI"
                ]
            ].copy()

            ndvi_chart["NDVI"] = pd.to_numeric(
                ndvi_chart["NDVI"],
                errors="coerce"
            )

            ndvi_chart = ndvi_chart.dropna(
                subset=[
                    "Date",
                    "NDVI"
                ]
            )

            if not ndvi_chart.empty:

                st.markdown(
                    "### 🌱 Vegetation Trend"
                )

                st.line_chart(
                    ndvi_chart.set_index("Date"),
                    height=300
                )

        # RAINFALL CHART

        if "Rainfall_mm" in chart_environmental.columns:

            rainfall_chart = chart_environmental[
                [
                    "Date",
                    "Rainfall_mm"
                ]
            ].copy()

            rainfall_chart["Rainfall_mm"] = pd.to_numeric(
                rainfall_chart["Rainfall_mm"],
                errors="coerce"
            )

            rainfall_chart = rainfall_chart.dropna(
                subset=[
                    "Date",
                    "Rainfall_mm"
                ]
            )

            if not rainfall_chart.empty:

                st.markdown(
                    "### 🌧️ Rainfall Trend"
                )

                st.line_chart(
                    rainfall_chart.set_index("Date"),
                    height=300
                )


# ============================================================
# WATER CONDITION HISTORY + AI FORECAST
# ============================================================

st.subheader(
    "📈 Water Condition History & AI Forecast"
)


if (
    not history.empty
    and "Year" in history.columns
    and "Month" in history.columns
    and "Average_NDWI" in history.columns
):

    chart_history = (
        history.copy()
    )

    chart_history["Date"] = pd.to_datetime(
        dict(
            year=pd.to_numeric(
                chart_history["Year"],
                errors="coerce"
            ),
            month=pd.to_numeric(
                chart_history["Month"],
                errors="coerce"
            ),
            day=1
        ),
        errors="coerce"
    )

    chart_history["Average_NDWI"] = pd.to_numeric(
        chart_history["Average_NDWI"],
        errors="coerce"
    )

    chart_history = chart_history.dropna(
        subset=[
            "Date",
            "Average_NDWI"
        ]
    )

    chart_history = chart_history.sort_values(
        "Date"
    )

    historical_chart = chart_history[
        [
            "Date",
            "Average_NDWI"
        ]
    ].rename(
        columns={
            "Average_NDWI":
            "Historical NDWI"
        }
    )

    # ========================================================
    # FORECAST
    # ========================================================

    if (
        not forecast.empty
        and "Predicted_NDWI" in forecast.columns
    ):

        chart_forecast = (
            forecast.copy()
        )

        if (
            "Year" in chart_forecast.columns
            and "Month" in chart_forecast.columns
        ):

            chart_forecast["Date"] = pd.to_datetime(
                dict(
                    year=pd.to_numeric(
                        chart_forecast["Year"],
                        errors="coerce"
                    ),
                    month=pd.to_numeric(
                        chart_forecast["Month"],
                        errors="coerce"
                    ),
                    day=1
                ),
                errors="coerce"
            )

        elif "Date" in chart_forecast.columns:

            chart_forecast["Date"] = pd.to_datetime(
                chart_forecast["Date"],
                errors="coerce"
            )

        else:

            chart_forecast["Date"] = pd.NaT

        chart_forecast["Predicted_NDWI"] = pd.to_numeric(
            chart_forecast["Predicted_NDWI"],
            errors="coerce"
        )

        chart_forecast = chart_forecast.dropna(
            subset=[
                "Date",
                "Predicted_NDWI"
            ]
        )

        forecast_chart = chart_forecast[
            [
                "Date",
                "Predicted_NDWI"
            ]
        ].rename(
            columns={
                "Predicted_NDWI":
                "AI Forecast"
            }
        )

        chart_data = pd.merge(
            historical_chart,
            forecast_chart,
            on="Date",
            how="outer"
        )

    else:

        chart_data = historical_chart

    chart_data = chart_data.sort_values(
        "Date"
    )

    chart_data = chart_data.set_index(
        "Date"
    )

    st.line_chart(
        chart_data,
        height=450
    )

    st.caption(
        "Historical NDWI represents observed water conditions. "
        "AI Forecast represents predicted future water conditions."
    )


else:

    st.info(
        "Historical NDWI data is not available for this lake."
    )


# ============================================================
# AI FORECAST & PREDICTION
# ============================================================

st.subheader(
    "🤖 AI Forecast & Prediction"
)

st.caption(
    "RiftGroundAI uses the historical NDWI record to estimate "
    "future water conditions and identify possible changes."
)


if (
    not history.empty
    and "Year" in history.columns
    and "Month" in history.columns
    and "Average_NDWI" in history.columns
):

    forecast_input = (
        history.copy()
    )

    forecast_input["Year"] = pd.to_numeric(
        forecast_input["Year"],
        errors="coerce"
    )

    forecast_input["Month"] = pd.to_numeric(
        forecast_input["Month"],
        errors="coerce"
    )

    forecast_input["Average_NDWI"] = pd.to_numeric(
        forecast_input["Average_NDWI"],
        errors="coerce"
    )

    forecast_input = forecast_input.dropna(
        subset=[
            "Year",
            "Month",
            "Average_NDWI"
        ]
    )

    forecast_input["Date"] = pd.to_datetime(
        dict(
            year=forecast_input["Year"].astype(int),
            month=forecast_input["Month"].astype(int),
            day=1
        ),
        errors="coerce"
    )

    forecast_input = forecast_input.dropna(
        subset=["Date"]
    )

    forecast_input = (
        forecast_input
        .sort_values("Date")
    )

    if len(forecast_input) >= 6:

        y = forecast_input[
            "Average_NDWI"
        ].values

        x = range(
            len(y)
        )

        # ====================================================
        # TREND-BASED FORECAST
        # ====================================================

        slope, intercept = np.polyfit(
            list(x),
            y,
            1
        )

        forecast_periods = 6

        future_x = np.arange(
            len(y),
            len(y) + forecast_periods
        )

        predicted_values = (
            intercept
            + slope * future_x
        )

        last_date = (
            forecast_input["Date"]
            .iloc[-1]
        )

        future_dates = pd.date_range(
            start=last_date + pd.DateOffset(months=1),
            periods=forecast_periods,
            freq="MS"
        )

        ai_forecast = pd.DataFrame(
            {
                "Date": future_dates,
                "Predicted_NDWI": predicted_values
            }
        )

        # ====================================================
        # DISPLAY FORECAST
        # ====================================================

        st.markdown(
            "### 🔮 Next 6-Month Water Condition Forecast"
        )

        f1, f2, f3 = st.columns(3)

        current_value = float(
            y[-1]
        )

        predicted_end = float(
            predicted_values[-1]
        )

        predicted_change = (
            predicted_end
            - current_value
        )

        with f1:

            st.metric(
                "Current NDWI",
                f"{current_value:.3f}"
            )

        with f2:

            st.metric(
                "6-Month Forecast",
                f"{predicted_end:.3f}"
            )

        with f3:

            st.metric(
                "Forecast Change",
                f"{predicted_change:+.3f}"
            )

        # ====================================================
        # FORECAST INTERPRETATION
        # ====================================================

        if predicted_change <= -0.05:

            st.error(
                "🚨 AI Warning: The forecast indicates "
                "a significant decline in water conditions "
                "over the next six months."
            )

        elif predicted_change < -0.02:

            st.warning(
                "⚠️ AI Alert: The forecast indicates "
                "a possible decline in water conditions."
            )

        elif predicted_change >= 0.05:

            st.success(
                "💧 AI Forecast: Water conditions are "
                "expected to improve over the next six months."
            )

        else:

            st.info(
                "ℹ️ AI Forecast: Water conditions are "
                "expected to remain relatively stable."
            )

        # ====================================================
        # FORECAST CHART
        # ====================================================

        historical_forecast_chart = forecast_input[
            [
                "Date",
                "Average_NDWI"
            ]
        ].rename(
            columns={
                "Average_NDWI":
                "Historical NDWI"
            }
        )

        forecast_chart = ai_forecast[
            [
                "Date",
                "Predicted_NDWI"
            ]
        ].rename(
            columns={
                "Predicted_NDWI":
                "AI Forecast"
            }
        )

        combined_forecast = pd.merge(
            historical_forecast_chart,
            forecast_chart,
            on="Date",
            how="outer"
        )

        combined_forecast = (
            combined_forecast
            .sort_values("Date")
            .set_index("Date")
        )

        st.line_chart(
            combined_forecast,
            height=400
        )

        st.caption(
            "Historical observations are shown together with "
            "the estimated future water-condition trend."
        )

        # ====================================================
        # FORECAST TABLE
        # ====================================================

        with st.expander(
            "🔮 View 6-Month AI Forecast"
        ):

            display_forecast = (
                ai_forecast.copy()
            )

            display_forecast["Date"] = (
                display_forecast["Date"]
                .dt.strftime("%Y-%m")
            )

            display_forecast[
                "Predicted_NDWI"
            ] = display_forecast[
                "Predicted_NDWI"
            ].round(3)

            st.dataframe(
                display_forecast,
                width="stretch"
            )

    else:

        st.info(
            "Not enough historical NDWI observations "
            "to generate an AI forecast."
        )


else:

    st.info(
        "Historical NDWI data is required to generate "
        "the AI forecast."
    )


# ============================================================
# RISK SCORE BREAKDOWN
# ============================================================

st.subheader(
    "🧩 Environmental Risk Score Breakdown"
)

st.caption(
    "The environmental risk score combines forecasted "
    "NDWI change, vegetation condition and rainfall "
    "condition to provide an early-warning indicator."
)


b1, b2, b3 = st.columns(3)


# ============================================================
# FORECASTED WATER-CONDITION STRESS
# ============================================================

with b1:

    st.metric(
        "💧 Forecasted Water-Condition Stress",
        f"{water_score}/50"
    )

    st.caption(
        f"Predicted NDWI change: {change:+.3f}"
    )


# ============================================================
# VEGETATION STRESS
# ============================================================

with b2:

    st.metric(
        "🌱 Vegetation Stress",
        f"{vegetation_score}/25"
    )

    st.caption(
        "Based on current vegetation conditions."
    )


# ============================================================
# RAINFALL STRESS
# ============================================================

with b3:

    st.metric(
        "🌧️ Rainfall Stress",
        f"{rainfall_score}/25"
    )

    st.caption(
        "Based on current rainfall conditions."
    )


# ============================================================
# IMPORTANT INTERPRETATION
# ============================================================

st.info(
    "💡 Important: NDWI is a satellite-derived indicator "
    "of water-related surface conditions. The water score "
    "does NOT represent a percentage loss of lake volume "
    "or lake depth. It represents forecasted stress based "
    "on the predicted change in NDWI."
)


# ============================================================
# AI FORECAST SUMMARY
# ============================================================

st.subheader(
    "🤖 AI Forecast Summary"
)

st.caption(
    "RiftGroundAI interprets satellite-derived NDWI "
    "together with vegetation and rainfall indicators "
    "to support early environmental decision-making."
)


# ============================================================
# WATER FORECAST
# ============================================================

if change <= -0.05:

    water_status = "🔴 Declining NDWI"

    water_message = (
        "The AI forecast indicates a decline in the "
        "satellite-derived NDWI indicator over the "
        "forecast period. This represents a potential "
        "change in water-related surface conditions and "
        "should not be interpreted as a direct measurement "
        "of decreasing lake volume."
    )

elif change >= 0.05:

    water_status = "🟢 Improving NDWI"

    water_message = (
        "The AI forecast indicates an improvement in the "
        "satellite-derived NDWI indicator over the "
        "forecast period, suggesting improving "
        "water-related surface conditions."
    )

else:

    water_status = "🟡 Stable NDWI"

    water_message = (
        "The AI forecast indicates relatively stable "
        "satellite-derived NDWI conditions over the "
        "forecast period."
    )


# ============================================================
# VEGETATION STATUS
# ============================================================

if latest_ndvi is None:

    vegetation_status = "⚪ No Data"

elif latest_ndvi < 0:

    vegetation_status = "🔴 Low"

elif latest_ndvi < 0.2:

    vegetation_status = "🟡 Moderate-Low"

elif latest_ndvi < 0.5:

    vegetation_status = "🟢 Moderate"

else:

    vegetation_status = "🟢 Healthy"


# ============================================================
# RAINFALL STATUS
# ============================================================

if latest_rainfall is None:

    rainfall_status = "⚪ No Data"

elif latest_rainfall < 20:

    rainfall_status = "🔴 Low"

elif latest_rainfall < 100:

    rainfall_status = "🟡 Moderate"

else:

    rainfall_status = "🟢 High"


# ============================================================
# SUMMARY CARDS
# ============================================================

s1, s2, s3 = st.columns(3)


with s1:

    st.metric(
        "💧 NDWI Forecast",
        water_status
    )


with s2:

    st.metric(
        "🌱 Vegetation",
        vegetation_status
    )


with s3:

    st.metric(
        "🌧️ Rainfall",
        rainfall_status
    )


# ============================================================
# AI INTERPRETATION
# ============================================================

st.markdown(
    "### 🧠 AI Interpretation"
)

st.write(
    water_message
)


if latest_ndvi is not None:

    if latest_ndvi < 0:

        st.write(
            "🌱 Vegetation activity is relatively low "
            "within the monitored area."
        )

    elif latest_ndvi < 0.5:

        st.write(
            "🌱 Vegetation activity is at a moderate level."
        )

    else:

        st.write(
            "🌱 Vegetation activity is relatively strong."
        )


if latest_rainfall is not None:

    if latest_rainfall < 20:

        st.write(
            "🌧️ Recent rainfall is relatively low, "
            "which may increase environmental stress."
        )

    elif latest_rainfall < 100:

        st.write(
            "🌧️ Recent rainfall is within a moderate range."
        )

    else:

        st.write(
            "🌧️ Recent rainfall is relatively high."
        )


# ============================================================
# RECOMMENDED ACTION
# ============================================================

st.markdown(
    "### 🎯 AI Recommended Action"
)

if risk_score >= 70:

    st.error(
        "🚨 HIGH PRIORITY: Increase environmental monitoring "
        "and investigate possible environmental stress "
        "indicated by the combined NDWI, vegetation and "
        "rainfall indicators."
    )

elif risk_score >= 40:

    st.warning(
        "⚠️ MODERATE PRIORITY: Continue close monitoring "
        "and assess changes in NDWI, vegetation and "
        "rainfall conditions."
    )

else:

    st.success(
        "✅ LOW PRIORITY: Continue routine environmental "
        "monitoring while tracking future NDWI, vegetation "
        "and rainfall changes."
    )

# ============================================================
# DECISION SUPPORT
# ============================================================

st.subheader(
    "🎯 Decision Support"
)

d1, d2 = st.columns(2)


with d1:

    st.markdown(
        "### 🔍 Why this score?"
    )

    if risk_score >= 70:

        st.write(
            "The projected water decline and/or environmental "
            "conditions indicate significant environmental "
            "stress. The lake should receive increased monitoring."
        )

    elif risk_score >= 40:

        st.write(
            "The indicators suggest moderate environmental "
            "stress. Continued monitoring is recommended."
        )

    else:

        st.write(
            "Current indicators suggest relatively stable "
            "conditions. Routine monitoring is recommended."
        )


with d2:

    st.markdown(
        "### 🚨 Recommended Action"
    )

    if risk_score >= 70:

        st.error(
            "Increase monitoring and investigate possible "
            "environmental stress."
        )

    elif risk_score >= 40:

        st.warning(
            "Continue close monitoring and assess changes "
            "in water and vegetation conditions."
        )

    else:

        st.success(
            "Continue routine environmental monitoring."
        )


# ============================================================
# ENVIRONMENTAL RISK MAP
# ============================================================

st.subheader(
    "🗺️ Rift Valley Environmental Risk Map"
)

st.caption(
    "Click a lake to view its environmental risk assessment "
    "and AI forecast."
)


m = folium.Map(
    location=[
        -0.5,
        36.2
    ],
    zoom_start=6,
    tiles="CartoDB dark_matter"
)


# ============================================================
# MAP MARKERS
# ============================================================

for lake_name, location in LAKES.items():

    lake_info = get_lake_information(
        lake_name
    )

    score = lake_info["risk_score"]
    level = lake_info["risk_level"]

    latest = lake_info["latest_ndwi"]
    predicted = lake_info["forecast_ndwi"]

    lake_change = lake_info["change"]

    color = get_risk_color(
        score
    )

    latest_text = (
        f"{latest:.3f}"
        if latest is not None
        else "N/A"
    )

    predicted_text = (
        f"{predicted:.3f}"
        if predicted is not None
        else "N/A"
    )

    change_text = (
        f"{lake_change:+.3f}"
    )

    if score >= 70:

        decision_text = (
            "Increase monitoring and investigate "
            "possible environmental stress."
        )

    elif score >= 40:

        decision_text = (
            "Continue close monitoring for emerging "
            "environmental changes."
        )

    else:

        decision_text = (
            "Continue routine monitoring."
        )

    popup_html = f"""
    <div style="
        width:320px;
        font-family:Arial;
        color:#222;
    ">

        <h2>🌍 {lake_name}</h2>

        <hr>

        <h3>🚨 Environmental Risk</h3>

        <h2 style="color:{color};">
            {level}
        </h2>

        <p>
            <b>Risk Score:</b>
            {score}/100
        </p>

        <hr>

        <h3>💧 Water Condition</h3>

        <p>
            <b>Latest NDWI:</b>
            {latest_text}
        </p>

        <p>
            <b>AI Forecast NDWI:</b>
            {predicted_text}
        </p>

        <p>
            <b>Projected Change:</b>
            {change_text}
        </p>

        <hr>

        <h3>🎯 Decision Support</h3>

        <p>
            {decision_text}
        </p>

    </div>
    """

    popup = folium.Popup(
        popup_html,
        max_width=380
    )

    folium.CircleMarker(
        location=[
            location["lat"],
            location["lon"]
        ],
        radius=10,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.9,
        weight=2,
        tooltip=(
            f"{lake_name} — "
            f"{level} "
            f"({score}/100)"
        ),
        popup=popup
    ).add_to(m)


# ============================================================
# MAP LEGEND
# ============================================================

legend_html = """

<div style="
position: fixed;
bottom: 40px;
left: 40px;
width: 190px;
background-color: white;
border: 2px solid grey;
z-index: 9999;
font-size: 14px;
padding: 10px;
color: black;
">

<b>🚨 Environmental Risk</b>
<br><br>

<span style="color:red;">●</span>
High Risk
<br><br>

<span style="color:orange;">●</span>
Moderate Risk
<br><br>

<span style="color:green;">●</span>
Low Risk

</div>

"""


m.get_root().html.add_child(
    folium.Element(
        legend_html
    )
)


# ============================================================
# DISPLAY MAP
# ============================================================

st_folium(
    m,
    width="100%",
    height=600,
    returned_objects=[]
)


# ============================================================
# DECISION PIPELINE
# ============================================================

st.subheader(
    "🧠 RiftGroundAI Decision Pipeline"
)

st.caption(
    "How RiftGroundAI transforms environmental observations "
    "into an actionable environmental risk decision."
)


p1, p2, p3, p4, p5 = st.columns(5)


with p1:

    st.markdown(
        """
        ### 🛰️ Observe

        RiftGroundAI collects satellite
        and environmental observations.
        """
    )


with p2:

    st.markdown(
        """
        ### 📊 Analyze

        Water, vegetation and rainfall
        conditions are analyzed.
        """
    )


with p3:

    st.markdown(
        """
        ### 🤖 Predict

        Machine learning estimates
        future water conditions.
        """
    )


with p4:

    st.markdown(
        """
        ### 🚨 Warn

        Multiple environmental indicators
        produce a composite risk score.
        """
    )


with p5:

    st.markdown(
        """
        ### 🎯 Act

        RiftGroundAI converts the risk
        assessment into a recommended action.
        """
    )


# ============================================================
# DATA TABLES
# ============================================================

with st.expander(
    "📋 View Historical NDWI Data"
):

    if not history.empty:

        st.dataframe(
            history,
            width="stretch"
        )

    else:

        st.info(
            "No historical NDWI data available."
        )


with st.expander(
    "🔮 View AI Forecast Data"
):

    if not forecast.empty:

        st.dataframe(
            forecast,
            width="stretch"
        )

    else:

        st.info(
            "No forecast data available."
        )


with st.expander(
    "🌱 View Environmental Data"
):

    if not environmental.empty:

        st.dataframe(
            environmental,
            width="stretch"
        )

    else:

        st.info(
            "No environmental data available."
        )


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(
    "RiftGroundAI • Sentinel-2 + CHIRPS + "
    "Earth Engine + Random Forest AI • "
    "Environmental Monitoring, Forecasting & Decision Support"
)
