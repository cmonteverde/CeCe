"""
Climate Data Sources Module for Climate Copilot

This module fetches climate data from various public sources and formats it
for use in the Climate Copilot application's visualizations and analysis tools.
Data sources include:
- DataHub.io climate datasets (Global temperature, CO2 levels, etc.)
- Kaggle climate datasets
- NASA Earth Observation data
- Other open climate data repositories
"""

import requests
import pandas as pd
import numpy as np
import json
import io
from datetime import datetime
import streamlit as st

# Cache data to avoid repeated API calls
@st.cache_data(ttl=3600)
def fetch_global_temperature_data():
    """
    Fetch global temperature anomaly data from DataHub
    
    Returns:
        DataFrame with global temperature anomaly data
    """
    url = "https://datahub.io/core/global-temp/r/anomalies.csv"
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        # Format data
        df.columns = [col.strip() for col in df.columns]
        return df
    except Exception as e:
        st.error(f"Error fetching global temperature data: {str(e)}")
        # Return empty DataFrame with expected columns
        return pd.DataFrame(columns=['Date', 'Mean', 'LandAverageTemperature', 'LandMaxTemperature', 'LandMinTemperature'])

@st.cache_data(ttl=3600)
def fetch_co2_data():
    """
    Fetch CO2 concentration data from DataHub
    
    Returns:
        DataFrame with CO2 PPM measurements
    """
    url = "https://datahub.io/core/co2-ppm/r/co2-mm-mlo.csv"
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        return df
    except Exception as e:
        st.error(f"Error fetching CO2 data: {str(e)}")
        return pd.DataFrame(columns=['Date', 'CO2'])

@st.cache_data(ttl=3600)
def fetch_sea_level_data():
    """
    Fetch sea level rise data from DataHub
    
    Returns:
        DataFrame with sea level measurements
    """
    url = "https://datahub.io/core/sea-level-rise/r/sea-level-rise.csv"
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        return df
    except Exception as e:
        st.error(f"Error fetching sea level data: {str(e)}")
        return pd.DataFrame(columns=['Year', 'GMSL'])

@st.cache_data(ttl=3600)
def fetch_glacier_data():
    """
    Fetch glacier mass balance data from DataHub
    
    Returns:
        DataFrame with glacier data
    """
    url = "https://datahub.io/core/glacier-mass-balance/r/glaciers.csv"
    try:
        response = requests.get(url)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        return df
    except Exception as e:
        st.error(f"Error fetching glacier data: {str(e)}")
        return pd.DataFrame(columns=['Year', 'Mean cumulative mass balance'])

def generate_global_temperature_grid(resolution=5):
    """
    Generate a grid of global temperature data for mapping
    
    Args:
        resolution: Grid resolution in degrees (default: 5)
        
    Returns:
        DataFrame with lat, lon, and temperature values
    """
    # Get temperature data
    temp_df = fetch_global_temperature_data()
    
    # Get most recent year with complete data
    if not temp_df.empty and 'Date' in temp_df.columns:
        # Extract the year from the Date column
        temp_df['Year'] = pd.to_datetime(temp_df['Date']).dt.year
        latest_year = temp_df['Year'].max()
        latest_data = temp_df[temp_df['Year'] == latest_year]
        
        # Calculate mean temperature for the latest year
        mean_temp = latest_data['Mean'].mean() if 'Mean' in latest_data.columns else 0
    else:
        mean_temp = 0
    
    # Create latitude and longitude grid
    lats = np.arange(-90, 91, resolution)
    lons = np.arange(-180, 181, resolution)
    
    # Create data points with temperature distribution (simplified model)
    data = []
    for lat in lats:
        # Model temperature distribution by latitude (simplified)
        # Warmer at equator, cooler at poles, with some random variation
        temp_factor = 1 - (abs(lat) / 90)**0.5  # Non-linear falloff from equator
        base_temp = mean_temp + 20 * temp_factor  # Higher base temp at equator
        
        for lon in lons:
            # Add some longitude variation (ocean vs land effects, etc)
            temp_variation = np.random.normal(0, 2)  # Random variation
            temp = base_temp + temp_variation
            
            data.append({
                'lat': lat,
                'lon': lon,
                'temperature': temp
            })
    
    return pd.DataFrame(data)

def get_climate_layer_data(layer_type="temperature"):
    """
    Get climate data formatted for map visualization
    
    Args:
        layer_type: Type of climate data to return
                   ("temperature", "co2", "sea_level", "glacier")
        
    Returns:
        Dictionary with data formatted for visualization
    """
    if layer_type == "temperature":
        # Return global temperature grid
        return generate_global_temperature_grid()
    
    elif layer_type == "co2":
        # Return CO2 data
        df = fetch_co2_data()
        if df.empty:
            return {"error": "No CO2 data available"}
        
        # Format data for visualization
        return {
            "type": "time_series",
            "title": "CO2 Concentration (PPM)",
            "data": df.to_dict(orient='records')
        }
    
    elif layer_type == "sea_level":
        # Return sea level data
        df = fetch_sea_level_data()
        if df.empty:
            return {"error": "No sea level data available"}
        
        # Format data for visualization
        return {
            "type": "time_series",
            "title": "Global Mean Sea Level (mm)",
            "data": df.to_dict(orient='records')
        }
    
    elif layer_type == "glacier":
        # Return glacier data
        df = fetch_glacier_data()
        if df.empty:
            return {"error": "No glacier data available"}
        
        # Format data for visualization
        return {
            "type": "time_series",
            "title": "Glacier Mass Balance",
            "data": df.to_dict(orient='records')
        }
    
    else:
        return {"error": f"Unsupported layer type: {layer_type}"}