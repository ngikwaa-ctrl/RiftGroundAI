import streamlit as st
import pandas as pd
import folium

from pathlib import Path
from streamlit_folium import st_folium


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
    """Find a data file in dashboard/data or project/data."""

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
# RISK SCORE
# ============================================================

def calculate_risk_score(ndwi_change):

    if ndwi_change <= -0.15:
        return 80

    elif ndwi_change <= -0.10:
        return 75

    elif ndwi_change <= -0.05:
        return 60

    elif ndwi_change <= -0.03:
        return 45

    elif ndwi_change < 0:
        return 30

    else:
        return 20


# ============================================================
# RISK LEVEL
# ============================================================

def get_risk_level(score):

    if score >= 70:
        return "HIGH"

    elif score >= 40:
        return "MODERATE"

    else:
        return "LOW"


# ============================================================
# RISK COLOR
# ============================================================

def get_risk_color(score):

    if score >= 70:
        return "red"

    elif score >= 40:
        return "orange"

    else:
        return "green"


# ============================================================
# GET LAKE INFORMATION
# ============================================================

def get_lake_information(lake):

    # --------------------------------------------------------
    # Files
    # --------------------------------------------------------

    history_file = find_data_file(
        f"{lake}_monthly_ndwi.csv"
    )

    forecast_file = find_data_file(
        f"{lake}_forecast.csv"
    )

    environmental_file = find_data_file(
        f"{lake}_environmental.csv"
    )

    # --------------------------------------------------------
    # Default values
    # --------------------------------------------------------

    latest_ndwi = None
    forecast_ndwi = None

    latest_ndvi = None
    latest_rainfall = None

    ndwi_change = 0.0

    # ========================================================
    # HISTORICAL NDWI
    # ========================================================

    if history_file is not None:

        try:

            history = pd.read_csv(history_file)

            if not history.empty:

                if "Average_NDWI" in history.columns:

                    valid_ndwi = history[
                        "Average_NDWI"
                    ].dropna()

                    if not valid_ndwi.empty:

                        latest_ndwi = float(
                            valid_ndwi.iloc[-1]
                        )

        except Exception:
            latest_ndwi = None

    # ========================================================
    # FORECAST NDWI
    # ========================================================

    if forecast_file is not None:

        try:

            forecast = pd.read_csv(forecast_file)

            if not forecast.empty:

                if "Predicted_NDWI" in forecast.columns:

                    valid_forecast = forecast[
                        "Predicted_NDWI"
                    ].dropna()

                    if not valid_forecast.empty:

                        forecast_ndwi = float(
                            valid_forecast.iloc[-1]
                        )

        except Exception:
            forecast_ndwi = None

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
                # Sort chronologically
                # ------------------------------------------------

                if (
                    "Year" in environmental.columns
                    and "Month" in environmental.columns
                ):

                    environmental = environmental.sort_values(
                        ["Year", "Month"]
                    )

                # ------------------------------------------------
                # Latest NDVI
                # ------------------------------------------------

                if "NDVI" in environmental.columns:

                    valid_ndvi = environmental[
                        "NDVI"
                    ].dropna()

                    if not valid_ndvi.empty:

                        latest_ndvi = float(
                            valid_ndvi.iloc[-1]
                        )

                # ------------------------------------------------
                # Latest Rainfall
                # ------------------------------------------------

                if "Rainfall_mm" in environmental.columns:

                    valid_rainfall = environmental[
                        "Rainfall_mm"
                    ].dropna()

                    if not valid_rainfall.empty:

                        latest_rainfall = float(
                            valid_rainfall.iloc[-1]
                        )

        except Exception:
            latest_ndvi = None
            latest_rainfall = None

    # ========================================================
    # PROJECTED CHANGE
    # ========================================================

    if (
        latest_ndwi is not None
        and forecast_ndwi is not None
    ):

        ndwi_change = (
            forecast_ndwi
            - latest_ndwi
        )

    # ========================================================
    # RISK
    # ========================================================

    risk_score = calculate_risk_score(
        ndwi_change
    )

    risk_level = get_risk_level(
        risk_score
    )

    return {
        "latest_ndwi": latest_ndwi,
        "forecast_ndwi": forecast_ndwi,
        "ndwi_change": ndwi_change,
        "latest_ndvi": latest_ndvi,
        "latest_rainfall": latest_rainfall,
        "risk_score": risk_score,
        "risk_level": risk_level
    }


# ============================================================
# RECOMMENDATION
# ============================================================

def get_recommendation(
    risk_score,
    ndwi_change,
    ndvi,
    rainfall
):

    if risk_score >= 70:

        return (
            "Increase monitoring and investigate "
            "possible environmental stress. "
            "Consider targeted field verification."
        )

    elif risk_score >= 40:

        return (
            "Continue close monitoring and assess "
            "changes in water and vegetation conditions."
        )

    else:

        return (
            "Continue routine monitoring. "
            "Current indicators do not show major stress."
        )


# ============================================================
# SHOW RISK MAP
# ============================================================

def show_risk_map():

    st.subheader(
        "🗺️ Rift Valley Environmental Risk Map"
    )

    st.caption(
        "Click any lake marker to view water, "
        "vegetation, rainfall, AI forecast and "
        "environmental risk information."
    )

    # ========================================================
    # CREATE MAP
    # ========================================================

    m = folium.Map(
        location=[
            -0.5,
            36.2
        ],
        zoom_start=6,
        tiles="CartoDB dark_matter"
    )

    # ========================================================
    # ADD LAKE MARKERS
    # ========================================================

    for lake, location in LAKES.items():

        info = get_lake_information(
            lake
        )

        # ----------------------------------------------------
        # Extract information
        # ----------------------------------------------------

        latest_ndwi = info[
            "latest_ndwi"
        ]

        forecast_ndwi = info[
            "forecast_ndwi"
        ]

        ndwi_change = info[
            "ndwi_change"
        ]

        latest_ndvi = info[
            "latest_ndvi"
        ]

        latest_rainfall = info[
            "latest_rainfall"
        ]

        risk_score = info[
            "risk_score"
        ]

        risk_level = info[
            "risk_level"
        ]

        # ----------------------------------------------------
        # Risk colour
        # ----------------------------------------------------

        risk_color = get_risk_color(
            risk_score
        )

        # ====================================================
        # FORMAT VALUES
        # ====================================================

        if latest_ndwi is not None:

            ndwi_text = (
                f"{latest_ndwi:.3f}"
            )

        else:

            ndwi_text = "N/A"

        if forecast_ndwi is not None:

            forecast_text = (
                f"{forecast_ndwi:.3f}"
            )

        else:

            forecast_text = "N/A"

        if latest_ndvi is not None:

            ndvi_text = (
                f"{latest_ndvi:.3f}"
            )

        else:

            ndvi_text = "N/A"

        if latest_rainfall is not None:

            rainfall_text = (
                f"{latest_rainfall:.1f} mm"
            )

        else:

            rainfall_text = "N/A"

        change_text = (
            f"{ndwi_change:+.3f}"
        )

        # ====================================================
        # TREND
        # ====================================================

        if ndwi_change > 0.03:

            trend_text = (
                "📈 Improving"
            )

        elif ndwi_change < -0.03:

            trend_text = (
                "📉 Declining"
            )

        else:

            trend_text = (
                "➡️ Relatively stable"
            )

        # ====================================================
        # RECOMMENDATION
        # ====================================================

        recommendation = get_recommendation(
            risk_score,
            ndwi_change,
            latest_ndvi,
            latest_rainfall
        )

        # ====================================================
        # POPUP
        # ====================================================

        popup_html = f"""
        <div style="
            width: 310px;
            font-family: Arial, sans-serif;
            color: #222;
        ">

            <h2 style="
                margin-bottom: 5px;
                color: #1769aa;
            ">
                🌍 {lake}
            </h2>

            <p style="
                margin-top: 0;
                color: #666;
            ">
                Rift Valley Environmental Monitor
            </p>

            <hr>

            <h3>
                🚨 Environmental Risk
            </h3>

            <div style="
                background: {risk_color};
                color: white;
                padding: 10px;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 18px;
            ">

                {risk_level}

                <br>

                <span style="
                    font-size: 14px;
                ">
                    Risk Score: {risk_score}/100
                </span>

            </div>

            <hr>

            <h3>
                💧 Water Condition
            </h3>

            <p>
                <b>Latest NDWI:</b>
                {ndwi_text}
            </p>

            <p>
                <b>AI Forecast NDWI:</b>
                {forecast_text}
            </p>

            <p>
                <b>Projected Change:</b>
                {change_text}
            </p>

            <p>
                <b>Water Trend:</b>
                {trend_text}
            </p>

            <hr>

            <h3>
                🌱 Vegetation
            </h3>

            <p>
                <b>Latest NDVI:</b>
                {ndvi_text}
            </p>

            <hr>

            <h3>
                🌧️ Rainfall
            </h3>

            <p>
                <b>Latest Rainfall:</b>
                {rainfall_text}
            </p>

            <hr>

            <h3>
                🎯 Decision Support
            </h3>

            <p>
                {recommendation}
            </p>

        </div>
        """

        # ====================================================
        # POPUP
        # ====================================================

        popup = folium.Popup(
            popup_html,
            max_width=370
        )

        # ====================================================
        # MARKER
        # ====================================================

        folium.CircleMarker(

            location=[
                location["lat"],
                location["lon"]
            ],

            radius=11,

            color=risk_color,

            fill=True,

            fill_color=risk_color,

            fill_opacity=0.9,

            weight=3,

            tooltip=(
                f"{lake} | "
                f"{risk_level} | "
                f"{risk_score}/100"
            ),

            popup=popup

        ).add_to(m)

    # ========================================================
    # MAP LEGEND
    # ========================================================

    legend_html = """

    <div style="
        position: fixed;
        bottom: 30px;
        left: 30px;

        z-index: 9999;

        background-color: white;

        padding: 14px 18px;

        border-radius: 10px;

        box-shadow:
            0 2px 10px rgba(0,0,0,0.3);

        font-family: Arial, sans-serif;

        font-size: 14px;
    ">

        <b>
            🚨 Environmental Risk
        </b>

        <br><br>

        <span style="
            color:red;
            font-size:20px;
        ">
            ●
        </span>

        High Risk

        <br>

        <span style="
            color:orange;
            font-size:20px;
        ">
            ●
        </span>

        Moderate Risk

        <br>

        <span style="
            color:green;
            font-size:20px;
        ">
            ●
        </span>

        Low Risk

    </div>

    """

    m.get_root().html.add_child(
        folium.Element(
            legend_html
        )
    )

    # ========================================================
    # DISPLAY MAP
    # ========================================================

    st_folium(
        m,
        width="100%",
        height=600,
        returned_objects=[]
    )
