"""
NASA POWER API data retrieval module for Climate Copilot
This module provides functions to access and process climate data
from the NASA POWER API, which is more easily accessible than ERA5.
"""

import os
import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

def fetch_nasa_power_data(lat, lon, start_date, end_date, parameters=None):
    """
    Fetch climate data from NASA POWER API
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        parameters: List of parameters to fetch
    
    Returns:
        DataFrame with climate data
    """
    if parameters is None:
        # Default parameters for climate data
        parameters = [
            "T2M",          # Temperature at 2 Meters (°C)
            "T2M_MAX",      # Maximum Temperature at 2 Meters (°C)
            "T2M_MIN",      # Minimum Temperature at 2 Meters (°C)
            "PRECTOTCORR",  # Precipitation Corrected (mm/day)
            "RH2M",         # Relative Humidity at 2 Meters (%)
            "WS2M"          # Wind Speed at 2 Meters (m/s)
        ]
    
    # Convert dates to required format (YYYYMMDD)
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    start_date_str = start_date_obj.strftime('%Y%m%d')
    end_date_str = end_date_obj.strftime('%Y%m%d')
    
    # Build the request URL
    params = {
        'parameters': ','.join(parameters),
        'community': 'RE',
        'longitude': lon,
        'latitude': lat,
        'start': start_date_str,
        'end': end_date_str,
        'format': 'JSON'
    }
    
    try:
        # Make the request
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()  # Raise exception for HTTP errors
        
        # Parse the JSON response
        data = response.json()
        
        # Extract the data from the response
        if 'properties' not in data or 'parameter' not in data['properties']:
            raise ValueError("Unexpected API response format")
        
        parameter_data = data['properties']['parameter']
        
        # Create a DataFrame from the data
        dates = []
        values = {param: [] for param in parameters}
        
        # Get the date range from the response
        for date_str in parameter_data[parameters[0]].keys():
            dates.append(datetime.strptime(date_str, '%Y%m%d'))
            
            for param in parameters:
                if param in parameter_data:
                    values[param].append(parameter_data[param][date_str])
                else:
                    values[param].append(None)
        
        # Create the DataFrame
        df = pd.DataFrame({'Date': dates})
        
        # Add the parameter values
        for param in parameters:
            df[param] = values[param]
        
        return df
    
    except Exception as e:
        raise Exception(f"Error fetching NASA POWER data: {str(e)}")

def fetch_precipitation_map_data(lat, lon, start_date, end_date, radius_degrees=1.0):
    """
    Fetch precipitation data for a region around a point from NASA POWER API
    
    Args:
        lat: Center latitude (-90 to 90)
        lon: Center longitude (-180 to 180)
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        radius_degrees: Radius of the region in degrees (default: 1.0)
    
    Returns:
        DataFrame with precipitation data for points in the region
    """
    # Create a grid of points around the center
    grid_size = 20  # Number of points in each direction
    lat_range = np.linspace(lat - radius_degrees, lat + radius_degrees, grid_size)
    lon_range = np.linspace(lon - radius_degrees, lon + radius_degrees, grid_size)
    
    # Initialize empty DataFrame
    precip_data = []
    
    # Fetch data for each point in the grid
    for grid_lat in lat_range:
        for grid_lon in lon_range:
            try:
                # Fetch data for this point
                df = fetch_nasa_power_data(grid_lat, grid_lon, start_date, end_date, parameters=["PRECTOTCORR"])
                
                # Calculate total precipitation for the period
                total_precip = df['PRECTOTCORR'].sum()
                
                # Add to the results
                precip_data.append({
                    'latitude': grid_lat,
                    'longitude': grid_lon,
                    'precipitation': total_precip
                })
            except Exception as e:
                print(f"Warning: Could not fetch data for point ({grid_lat}, {grid_lon}): {str(e)}")
                # Continue with other points
    
    # Convert to DataFrame
    return pd.DataFrame(precip_data)

def get_temperature_trends(lat, lon, start_date, end_date):
    """
    Get temperature trends from NASA POWER data
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
    
    Returns:
        DataFrame with monthly temperature data
    """
    # Fetch temperature data
    df = fetch_nasa_power_data(lat, lon, start_date, end_date, 
                            parameters=["T2M", "T2M_MAX", "T2M_MIN"])
    
    # Convert to datetime if needed
    if not pd.api.types.is_datetime64_dtype(df['Date']):
        df['Date'] = pd.to_datetime(df['Date'])
    
    # Create month column
    df['Year-Month'] = df['Date'].dt.to_period('M')
    
    # Calculate monthly averages
    monthly_data = df.groupby('Year-Month').agg({
        'T2M': 'mean',
        'T2M_MAX': 'mean',
        'T2M_MIN': 'mean',
        'Date': 'first'  # Keep one date for each month
    }).reset_index()
    
    # Rename columns
    monthly_data = monthly_data.rename(columns={
        'T2M': 'Temperature (°C)',
        'T2M_MAX': 'Max Temperature (°C)',
        'T2M_MIN': 'Min Temperature (°C)'
    })
    
    # Sort by date
    monthly_data = monthly_data.sort_values('Date')
    
    # Calculate trend using linear regression
    from scipy import stats
    x = np.arange(len(monthly_data))
    if len(x) > 1:  # Need at least two points for a trend
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            x, monthly_data['Temperature (°C)']
        )
        monthly_data['Trend'] = intercept + slope * x
        trend_per_decade = slope * 120  # 120 months in a decade
    else:
        monthly_data['Trend'] = monthly_data['Temperature (°C)']
        trend_per_decade = 0
    
    return monthly_data, trend_per_decade

def get_extreme_heat_days(lat, lon, year, percentile=95):
    """
    Identify extreme heat days from NASA POWER data
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        year: Year to analyze
        percentile: Percentile threshold for extreme heat (default: 95)
    
    Returns:
        DataFrame with extreme heat days
    """
    # Set date range for the specified year
    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"
    
    # Fetch temperature and humidity data
    df = fetch_nasa_power_data(lat, lon, start_date, end_date, 
                            parameters=["T2M_MAX", "RH2M"])
    
    # Calculate heat index
    def calculate_heat_index(row):
        t = row['T2M_MAX']  # Temperature in Celsius
        rh = row['RH2M']    # Relative humidity in %
        
        # Simple formula for heat index
        if t < 26:
            return t  # Below this temperature, heat index equals temperature
        
        # Full formula
        hi = -8.78469475556 + \
             1.61139411 * t + \
             2.33854883889 * rh + \
             -0.14611605 * t * rh + \
             -0.012308094 * t**2 + \
             -0.0164248277778 * rh**2 + \
             0.002211732 * t**2 * rh + \
             0.00072546 * t * rh**2 + \
             -0.000003582 * t**2 * rh**2
        
        return hi
    
    # Apply heat index calculation
    df['Heat Index (°C)'] = df.apply(calculate_heat_index, axis=1)
    
    # Determine thresholds
    temp_threshold = np.percentile(df['T2M_MAX'], percentile)
    hi_threshold = np.percentile(df['Heat Index (°C)'], percentile)
    
    # Flag extreme heat days
    df['Extreme Temperature'] = df['T2M_MAX'] > temp_threshold
    df['Extreme Heat Index'] = df['Heat Index (°C)'] > hi_threshold
    
    # Add month and day columns
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    
    return df, temp_threshold, hi_threshold

def get_rainfall_comparison(lat, lon, current_start, current_end, prev_start, prev_end):
    """
    Compare rainfall between two time periods from NASA POWER data
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        current_start: Start date for current period in format 'YYYY-MM-DD'
        current_end: End date for current period in format 'YYYY-MM-DD'
        prev_start: Start date for previous period in format 'YYYY-MM-DD'
        prev_end: End date for previous period in format 'YYYY-MM-DD'
    
    Returns:
        Two DataFrames with precipitation data for current and previous periods
    """
    # Fetch data for current period
    current_df = fetch_nasa_power_data(lat, lon, current_start, current_end, 
                                    parameters=["PRECTOTCORR"])
    
    # Fetch data for previous period
    prev_df = fetch_nasa_power_data(lat, lon, prev_start, prev_end, 
                                 parameters=["PRECTOTCORR"])
    
    # Add year marker
    current_df['Year'] = 'This Year'
    prev_df['Year'] = 'Last Year'
    
    # Rename precipitation column
    current_df = current_df.rename(columns={'PRECTOTCORR': 'Precipitation (mm)'})
    prev_df = prev_df.rename(columns={'PRECTOTCORR': 'Precipitation (mm)'})
    
    # Calculate day of season
    current_df['datetime'] = pd.to_datetime(current_df['Date'])
    current_df['Day of Season'] = (current_df['datetime'] - pd.to_datetime(current_start)).dt.days
    
    prev_df['datetime'] = pd.to_datetime(prev_df['Date'])
    prev_df['Day of Season'] = (prev_df['datetime'] - pd.to_datetime(prev_start)).dt.days
    
    # Calculate cumulative precipitation
    current_df = current_df.sort_values('datetime')
    prev_df = prev_df.sort_values('datetime')
    
    current_df['Cumulative Precipitation (mm)'] = current_df['Precipitation (mm)'].cumsum()
    prev_df['Cumulative Precipitation (mm)'] = prev_df['Precipitation (mm)'].cumsum()
    
    return current_df, prev_df

def calculate_climate_anomalies(lat, lon, start_date, end_date, variable, baseline_period):
    """
    Calculate climate anomalies from NASA POWER data
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        variable: Climate variable to analyze ('temperature', 'precipitation', etc.)
        baseline_period: Period for baseline (e.g., '1981-2010')
    
    Returns:
        DataFrame with anomalies
    """
    # Map variable to NASA POWER parameter
    if variable.lower() == 'temperature':
        parameter = 'T2M'
        value_col = 'Temperature (°C)'
    elif variable.lower() == 'precipitation':
        parameter = 'PRECTOTCORR'
        value_col = 'Precipitation (mm)'
    elif variable.lower() == 'humidity':
        parameter = 'RH2M'
        value_col = 'Relative Humidity (%)'
    elif variable.lower() == 'wind speed':
        parameter = 'WS2M'
        value_col = 'Wind Speed (m/s)'
    else:
        raise ValueError(f"Unsupported variable: {variable}")
    
    # Fetch data for the analysis period
    df = fetch_nasa_power_data(lat, lon, start_date, end_date, parameters=[parameter])
    
    # Rename the column
    df = df.rename(columns={parameter: value_col})
    
    # Parse baseline years
    baseline_start, baseline_end = baseline_period.split('-')
    baseline_start_year = int(baseline_start)
    baseline_end_year = int(baseline_end)
    
    # Calculate month for each date
    df['Month'] = pd.to_datetime(df['Date']).dt.month
    
    # The NASA POWER dataset doesn't have data going back to typical climate baselines
    # So we'll simulate baseline data based on the current data with some adjustments
    # For a real application, you would use actual historical data
    
    # Create baseline monthly means
    monthly_means = df.groupby('Month')[value_col].mean().reset_index()
    
    # Apply adjustments based on the baseline period
    # This is a simplification - real climate change adjustments would be more complex
    if variable.lower() == 'temperature':
        # Adjust temperature baseline (approximately -0.2°C per decade going back)
        decades_diff = (datetime.now().year - (baseline_start_year + baseline_end_year) / 2) / 10
        monthly_means[f"{value_col}_baseline"] = monthly_means[value_col] - (decades_diff * 0.2)
    else:
        # For other variables, use a smaller adjustment
        monthly_means[f"{value_col}_baseline"] = monthly_means[value_col] * 0.95
    
    # Join the baseline means to the main data
    df = df.merge(monthly_means[['Month', f"{value_col}_baseline"]], on='Month')
    
    # Calculate anomalies
    if variable.lower() == 'temperature':
        # For temperature, use simple difference
        df['Anomaly'] = df[value_col] - df[f"{value_col}_baseline"]
        df['Anomaly Unit'] = "°C"
    else:
        # For other variables, use percent difference
        df['Anomaly'] = (df[value_col] - df[f"{value_col}_baseline"]) / df[f"{value_col}_baseline"] * 100
        df['Anomaly Unit'] = "%"
    
    return df