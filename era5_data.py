"""
ERA5 data retrieval module for Climate Copilot
This module provides functions to access and process ERA5 reanalysis data
from the Copernicus Climate Data Store (CDS).
"""

import os
import time
import cdsapi
import xarray as xr
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Create CDS client
def get_cds_client():
    """
    Initialize and return a CDS API client
    
    For this to work, the user needs to have a CDS API key.
    """
    try:
        client = cdsapi.Client()
        return client
    except Exception as e:
        raise Exception(f"Failed to initialize CDS API client: {str(e)}")

def fetch_era5_data(lat, lon, start_date, end_date, variables=None):
    """
    Fetch ERA5 reanalysis data for a specific location and time period
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        variables: List of ERA5 variables to retrieve (default: temperature and precipitation)
    
    Returns:
        DataFrame with ERA5 data
    """
    if variables is None:
        variables = ['2m_temperature', 'total_precipitation']
    
    # Format dates for CDS API
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Format dates for request
    start_year = start_date_obj.year
    start_month = start_date_obj.month
    start_day = start_date_obj.day
    
    end_year = end_date_obj.year
    end_month = end_date_obj.month
    end_day = end_date_obj.day
    
    # Years, months, days for request
    years = [str(year) for year in range(start_year, end_year + 1)]
    months = [f"{month:02d}" for month in range(1, 13)]
    days = [f"{day:02d}" for day in range(1, 32)]
    
    # Initialize CDS client
    try:
        client = get_cds_client()
    except Exception as e:
        raise Exception(f"Failed to initialize CDS client: {str(e)}")
    
    # Prepare output file
    output_file = 'era5_data.nc'
    
    try:
        # Request data from CDS
        client.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'format': 'netcdf',
                'variable': variables,
                'year': years,
                'month': months,
                'day': days,
                'time': ['00:00', '06:00', '12:00', '18:00'],
                'area': [lat + 0.5, lon - 0.5, lat - 0.5, lon + 0.5],  # North, West, South, East
            },
            output_file
        )
        
        # Read the netCDF file
        ds = xr.open_dataset(output_file)
        
        # Filter to the exact date range
        ds = ds.sel(time=slice(start_date, end_date))
        
        # Extract data for the exact lat/lon
        ds = ds.sel(latitude=lat, longitude=lon, method='nearest')
        
        # Convert to pandas DataFrame
        df = ds.to_dataframe().reset_index()
        
        # Clean up the file
        os.remove(output_file)
        
        return process_era5_data(df)
    
    except Exception as e:
        # If file exists but there was an error, clean up
        if os.path.exists(output_file):
            os.remove(output_file)
        raise Exception(f"Error fetching ERA5 data: {str(e)}")

def process_era5_data(df):
    """
    Process raw ERA5 data into a more usable format
    
    Args:
        df: DataFrame with raw ERA5 data
    
    Returns:
        Processed DataFrame
    """
    # Rename columns to more friendly names
    renames = {
        't2m': 'Temperature (K)',
        '2m_temperature': 'Temperature (K)',
        'tp': 'Precipitation (m)',
        'total_precipitation': 'Precipitation (m)'
    }
    
    # Apply renames for columns that exist
    for old_name, new_name in renames.items():
        if old_name in df.columns:
            df = df.rename(columns={old_name: new_name})
    
    # Convert units
    if 'Temperature (K)' in df.columns:
        # Convert Kelvin to Celsius
        df['Temperature (°C)'] = df['Temperature (K)'] - 273.15
        df = df.drop(columns=['Temperature (K)'])
    
    if 'Precipitation (m)' in df.columns:
        # Convert meters to millimeters
        df['Precipitation (mm)'] = df['Precipitation (m)'] * 1000
        df = df.drop(columns=['Precipitation (m)'])
        
        # ERA5 precipitation is cumulative, so we need to calculate daily values
        # First sort by time
        df = df.sort_values('time')
        
        # Calculate the time difference in hours
        df['time_diff'] = df['time'].diff().dt.total_seconds() / 3600
        
        # For the first row, we'll assume it's the same as the step size
        if len(df) > 1:
            df.loc[df.index[0], 'time_diff'] = df.loc[df.index[1], 'time_diff']
        else:
            df.loc[df.index[0], 'time_diff'] = 24  # Assume daily data if only one row
        
        # Calculate precipitation rate
        df['Precipitation Rate (mm/hour)'] = df['Precipitation (mm)'] / df['time_diff']
        
        # Group by day and sum precipitation
        df['Date'] = df['time'].dt.date
        daily_precip = df.groupby('Date')['Precipitation (mm)'].sum().reset_index()
        
        # Keep track of daily precipitation
        df = df.merge(daily_precip, on='Date', suffixes=('', '_daily'))
        df = df.rename(columns={'Precipitation (mm)_daily': 'Daily Precipitation (mm)'})
        
        # Clean up
        df = df.drop(columns=['time_diff'])
    
    return df

def fetch_era5_precipitation_map(lat, lon, start_date, end_date, radius_degrees=1.0):
    """
    Fetch ERA5 precipitation data for a region around a point
    
    Args:
        lat: Center latitude (-90 to 90)
        lon: Center longitude (-180 to 180)
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        radius_degrees: Radius of the region in degrees (default: 1.0)
    
    Returns:
        xarray Dataset with precipitation data for the region
    """
    # Format dates for CDS API
    start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    end_date_obj = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Format dates for request
    start_year = start_date_obj.year
    start_month = start_date_obj.month
    start_day = start_date_obj.day
    
    end_year = end_date_obj.year
    end_month = end_date_obj.month
    end_day = end_date_obj.day
    
    # Years, months, days for request
    years = [str(year) for year in range(start_year, end_year + 1)]
    months = [f"{month:02d}" for month in range(1, 13)]
    days = [f"{day:02d}" for day in range(1, 32)]
    
    # Initialize CDS client
    try:
        client = get_cds_client()
    except Exception as e:
        raise Exception(f"Failed to initialize CDS client: {str(e)}")
    
    # Calculate region bounds
    north = min(90, lat + radius_degrees)
    south = max(-90, lat - radius_degrees)
    west = max(-180, lon - radius_degrees)
    east = min(180, lon + radius_degrees)
    
    # Prepare output file
    output_file = 'era5_precip_map.nc'
    
    try:
        # Request data from CDS
        client.retrieve(
            'reanalysis-era5-single-levels',
            {
                'product_type': 'reanalysis',
                'format': 'netcdf',
                'variable': ['total_precipitation'],
                'year': years,
                'month': months,
                'day': days,
                'time': ['00:00', '06:00', '12:00', '18:00'],
                'area': [north, west, south, east],  # North, West, South, East
            },
            output_file
        )
        
        # Read the netCDF file
        ds = xr.open_dataset(output_file)
        
        # Filter to the exact date range
        ds = ds.sel(time=slice(start_date, end_date))
        
        # Sum precipitation over time
        total_precip = ds.sum(dim='time')
        
        # Convert units from meters to millimeters
        if 'tp' in total_precip:
            total_precip['tp'] = total_precip['tp'] * 1000
            total_precip = total_precip.rename({'tp': 'total_precipitation_mm'})
        elif 'total_precipitation' in total_precip:
            total_precip['total_precipitation'] = total_precip['total_precipitation'] * 1000
            total_precip = total_precip.rename({'total_precipitation': 'total_precipitation_mm'})
        
        # Clean up the file
        os.remove(output_file)
        
        return total_precip
    
    except Exception as e:
        # If file exists but there was an error, clean up
        if os.path.exists(output_file):
            os.remove(output_file)
        raise Exception(f"Error fetching ERA5 precipitation map: {str(e)}")

def get_era5_temperature_trends(lat, lon, start_date, end_date):
    """
    Get temperature trends from ERA5 data
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
    
    Returns:
        DataFrame with monthly temperature data and trends
    """
    # Fetch raw ERA5 data
    df = fetch_era5_data(lat, lon, start_date, end_date, variables=['2m_temperature'])
    
    # Ensure we have temperature data
    if 'Temperature (°C)' not in df.columns:
        raise Exception("Temperature data not found in ERA5 response")
    
    # Resample to monthly data for trends
    df['Month'] = df['time'].dt.to_period('M')
    monthly_temp = df.groupby('Month')['Temperature (°C)'].agg(['mean', 'min', 'max']).reset_index()
    monthly_temp['Month'] = monthly_temp['Month'].dt.to_timestamp()
    
    # Rename columns
    monthly_temp = monthly_temp.rename(columns={
        'mean': 'Temperature (°C)',
        'min': 'Min Temperature (°C)',
        'max': 'Max Temperature (°C)'
    })
    
    # Calculate the trend
    x = np.arange(len(monthly_temp))
    if len(x) > 1:  # Need at least two points for a trend
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            x, monthly_temp['Temperature (°C)']
        )
        monthly_temp['Trend'] = intercept + slope * x
        trend_per_decade = slope * 120  # 120 months in a decade
    else:
        monthly_temp['Trend'] = monthly_temp['Temperature (°C)']
        trend_per_decade = 0
    
    return monthly_temp, trend_per_decade

def get_era5_extreme_heat(lat, lon, year, percentile=95):
    """
    Identify extreme heat days from ERA5 data
    
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
    
    # Fetch raw ERA5 data with temperature and dewpoint
    df = fetch_era5_data(lat, lon, start_date, end_date, 
                       variables=['2m_temperature', '2m_dewpoint_temperature'])
    
    # Ensure we have temperature data
    if 'Temperature (°C)' not in df.columns:
        raise Exception("Temperature data not found in ERA5 response")
    
    # Calculate daily maximum temperature
    df['Date'] = df['time'].dt.date
    daily_max = df.groupby('Date')['Temperature (°C)'].max().reset_index()
    daily_max = daily_max.rename(columns={'Temperature (°C)': 'Max Temperature (°C)'})
    
    # Calculate heat index if we have dewpoint data
    if '2m_dewpoint_temperature' in df.columns or 'd2m' in df.columns:
        # Convert dewpoint from K to C if necessary
        if 'd2m' in df.columns:
            df['Dewpoint (°C)'] = df['d2m'] - 273.15
        elif '2m_dewpoint_temperature' in df.columns:
            df['Dewpoint (°C)'] = df['2m_dewpoint_temperature'] - 273.15
        
        # Calculate relative humidity from temperature and dewpoint
        df['Relative Humidity (%)'] = 100 * (
            np.exp((17.625 * df['Dewpoint (°C)']) / (243.04 + df['Dewpoint (°C)'])) /
            np.exp((17.625 * df['Temperature (°C)']) / (243.04 + df['Temperature (°C)']))
        )
        
        # Calculate heat index
        def calculate_heat_index(row):
            t = row['Temperature (°C)']
            rh = row['Relative Humidity (%)']
            
            # Convert to Fahrenheit for the formula
            t_f = t * 9/5 + 32
            
            # Simple formula for lower temperatures
            if t_f < 80:
                return t
            
            # Full formula for higher temperatures
            hi = -42.379 + 2.04901523 * t_f + 10.14333127 * rh
            hi = hi - 0.22475541 * t_f * rh - 0.00683783 * t_f**2
            hi = hi - 0.05481717 * rh**2 + 0.00122874 * t_f**2 * rh
            hi = hi + 0.00085282 * t_f * rh**2 - 0.00000199 * t_f**2 * rh**2
            
            # Convert back to Celsius
            hi_c = (hi - 32) * 5/9
            return hi_c
        
        df['Heat Index (°C)'] = df.apply(calculate_heat_index, axis=1)
        
        # Get daily maximum heat index
        daily_heat_index = df.groupby('Date')['Heat Index (°C)'].max().reset_index()
        daily_max = daily_max.merge(daily_heat_index, on='Date')
    else:
        # If no dewpoint data, just use temperature
        daily_max['Heat Index (°C)'] = daily_max['Max Temperature (°C)']
    
    # Determine extreme heat threshold
    temp_threshold = np.percentile(daily_max['Max Temperature (°C)'], percentile)
    hi_threshold = np.percentile(daily_max['Heat Index (°C)'], percentile)
    
    # Flag extreme heat days
    daily_max['Extreme Temperature'] = daily_max['Max Temperature (°C)'] > temp_threshold
    daily_max['Extreme Heat Index'] = daily_max['Heat Index (°C)'] > hi_threshold
    
    # Create a date column that's datetime
    daily_max['datetime'] = pd.to_datetime(daily_max['Date'])
    daily_max['Month'] = daily_max['datetime'].dt.month
    daily_max['Day'] = daily_max['datetime'].dt.day
    
    return daily_max, temp_threshold, hi_threshold

def get_era5_rainfall_comparison(lat, lon, current_start, current_end, prev_start, prev_end):
    """
    Compare rainfall between two time periods from ERA5 data
    
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
    current_df = fetch_era5_data(lat, lon, current_start, current_end, variables=['total_precipitation'])
    
    # Fetch data for previous period
    prev_df = fetch_era5_data(lat, lon, prev_start, prev_end, variables=['total_precipitation'])
    
    # Ensure we have precipitation data
    if 'Daily Precipitation (mm)' not in current_df.columns or 'Daily Precipitation (mm)' not in prev_df.columns:
        raise Exception("Precipitation data not found in ERA5 response")
    
    # Add year marker
    current_df['Year'] = 'This Year'
    prev_df['Year'] = 'Last Year'
    
    # Calculate day of season
    current_df['datetime'] = pd.to_datetime(current_df['Date'])
    current_df['Day of Season'] = (current_df['datetime'] - pd.to_datetime(current_start)).dt.days
    
    prev_df['datetime'] = pd.to_datetime(prev_df['Date'])
    prev_df['Day of Season'] = (prev_df['datetime'] - pd.to_datetime(prev_start)).dt.days
    
    # Calculate cumulative precipitation
    current_df = current_df.sort_values('datetime')
    prev_df = prev_df.sort_values('datetime')
    
    current_df['Cumulative Precipitation (mm)'] = current_df['Daily Precipitation (mm)'].cumsum()
    prev_df['Cumulative Precipitation (mm)'] = prev_df['Daily Precipitation (mm)'].cumsum()
    
    return current_df, prev_df

def calculate_era5_anomalies(lat, lon, start_date, end_date, variable, baseline_period):
    """
    Calculate climate anomalies from ERA5 data
    
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
    # Determine ERA5 variable name based on input
    if variable.lower() == 'temperature':
        era5_var = ['2m_temperature']
        value_col = 'Temperature (°C)'
    elif variable.lower() == 'precipitation':
        era5_var = ['total_precipitation']
        value_col = 'Daily Precipitation (mm)'
    elif variable.lower() == 'humidity':
        era5_var = ['2m_dewpoint_temperature', '2m_temperature']
        # We'll calculate relative humidity from temperature and dewpoint
        value_col = 'Relative Humidity (%)'
    elif variable.lower() == 'wind speed':
        era5_var = ['10m_u_component_of_wind', '10m_v_component_of_wind']
        # We'll calculate wind speed from U and V components
        value_col = 'Wind Speed (m/s)'
    else:
        raise ValueError(f"Unsupported variable: {variable}")
    
    # Fetch data for the analysis period
    df = fetch_era5_data(lat, lon, start_date, end_date, variables=era5_var)
    
    # Parse baseline years
    baseline_start, baseline_end = baseline_period.split('-')
    baseline_start_year = int(baseline_start)
    baseline_end_year = int(baseline_end)
    
    # Set baseline period dates to cover all months
    baseline_start_date = f"{baseline_start_year}-01-01"
    baseline_end_date = f"{baseline_end_year}-12-31"
    
    # Trying to fetch baseline data might be too much data at once
    # Let's fetch it year by year
    baseline_data = []
    for year in range(baseline_start_year, baseline_end_year + 1):
        try:
            year_start = f"{year}-01-01"
            year_end = f"{year}-12-31"
            year_data = fetch_era5_data(lat, lon, year_start, year_end, variables=era5_var)
            baseline_data.append(year_data)
        except Exception as e:
            print(f"Warning: Could not fetch baseline data for {year}: {str(e)}")
            # Continue with other years
            continue
    
    if not baseline_data:
        raise Exception("Could not fetch any baseline data")
    
    # Combine all baseline years
    baseline_df = pd.concat(baseline_data)
    
    # Calculate monthly means for the baseline
    baseline_df['Month'] = baseline_df['time'].dt.month
    baseline_monthly_means = baseline_df.groupby('Month')[value_col].mean().reset_index()
    
    # Add month to the analysis data
    df['Month'] = df['time'].dt.month
    
    # Join the baseline means
    df = df.merge(baseline_monthly_means, on='Month', suffixes=('', '_baseline'))
    
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