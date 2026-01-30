"""
NOAA National Weather Service (NWS) API Module
Interacts with api.weather.gov to fetch real-time weather data for US locations.
"""

import requests
import streamlit as st
import pandas as pd
from datetime import datetime

USER_AGENT = "(ClimateCopilot/1.0, research-prototype)"
BASE_URL = "https://api.weather.gov"

@st.cache_data(ttl=3600)
def get_grid_point(lat, lon):
    """
    Get NWS grid point metadata for a given lat/lon.
    Returns None if location is not supported (e.g., outside US).
    """
    url = f"{BASE_URL}/points/{lat},{lon}"
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            return None # Location likely outside US coverage
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching grid point: {e}")
        return None

@st.cache_data(ttl=1800) # Cache for 30 mins
def get_forecast(lat, lon):
    """
    Fetch the 7-day forecast for a US location.
    """
    grid_data = get_grid_point(lat, lon)
    if not grid_data:
        return {"error": "Location not supported by NWS (US only)."}

    try:
        properties = grid_data.get("properties", {})
        forecast_url = properties.get("forecast")

        if not forecast_url:
            return {"error": "No forecast URL found for this location."}

        headers = {"User-Agent": USER_AGENT}
        response = requests.get(forecast_url, headers=headers, timeout=10)
        response.raise_for_status()

        return response.json()
    except Exception as e:
        return {"error": f"Error fetching forecast: {str(e)}"}

@st.cache_data(ttl=300) # Cache for 5 mins (alerts are urgent)
def get_active_alerts(lat, lon):
    """
    Fetch active weather alerts for a specific point.
    """
    url = f"{BASE_URL}/alerts/active?point={lat},{lon}"
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return {"error": f"Error fetching alerts: {str(e)}"}

def parse_forecast_to_df(forecast_json):
    """
    Convert the raw forecast JSON into a simple DataFrame for display.
    """
    if "properties" not in forecast_json or "periods" not in forecast_json["properties"]:
        return pd.DataFrame()

    periods = forecast_json["properties"]["periods"]

    data = []
    for p in periods:
        data.append({
            "Period": p.get("name"),
            "Temperature": f"{p.get('temperature')}°{p.get('temperatureUnit')}",
            "Wind": f"{p.get('windSpeed')} {p.get('windDirection')}",
            "Forecast": p.get("shortForecast"),
            "Details": p.get("detailedForecast")
        })

    return pd.DataFrame(data)
