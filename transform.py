import pandas as pd
import numpy as np
import folium
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import base64
import json
import requests
from typing import Dict, List, Tuple, Optional, Union
import climate_algorithms

# NASA POWER API client
def fetch_nasa_power_data(lat: float, lon: float, start_date: str, end_date: str, 
                         parameters: List[str] = None) -> pd.DataFrame:
    """
    Fetch climate data from NASA POWER API
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        start_date: Start date in format 'YYYYMMDD'
        end_date: End date in format 'YYYYMMDD'
        parameters: List of parameters to fetch (e.g., T2M, PRECTOT)
        
    Returns:
        DataFrame with requested climate data
    """
    if parameters is None:
        parameters = ["T2M", "T2M_MAX", "T2M_MIN", "PRECTOT", "RH2M", "WS2M"]
    
    base_url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    params = {
        "start": start_date,
        "end": end_date,
        "latitude": lat,
        "longitude": lon,
        "community": "RE",
        "parameters": ",".join(parameters),
        "format": "JSON",
        "user": "CeCeClimateApp"
    }
    
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise exception for bad status codes
        
        data = response.json()
        
        # Extract the data from the response
        if "properties" in data and "parameter" in data["properties"]:
            parameter_data = data["properties"]["parameter"]
            
            # Create a dataframe from the parameter data
            df = pd.DataFrame()
            
            # Get the dates
            dates = list(parameter_data[parameters[0]].keys())
            df["DATE"] = [datetime.strptime(date, "%Y%m%d") for date in dates]
            
            # Add each parameter as a column
            for param in parameters:
                if param in parameter_data:
                    df[param] = [parameter_data[param][date] for date in dates]
            
            return df
        else:
            raise ValueError("Unexpected API response format")
    
    except Exception as e:
        raise Exception(f"Error fetching NASA POWER data: {str(e)}")

# Data cleaning functions
def detect_and_convert_date_column(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect date columns and convert to datetime
    """
    for col in df.columns:
        # Check if column name contains date-related terms
        if any(date_term in col.lower() for date_term in ['date', 'time', 'day', 'year', 'month']):
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                # If more than 90% of values were successfully converted, consider it a date column
                if df[col].notnull().mean() > 0.9:
                    print(f"Converted {col} to datetime")
            except:
                pass
    return df

def remove_outliers(df: pd.DataFrame, column: str, method: str = 'iqr', threshold: float = 3.0) -> pd.DataFrame:
    """
    Remove outliers from a column using IQR or Z-score method
    """
    if method == 'iqr':
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - threshold * IQR
        upper_bound = Q3 + threshold * IQR
        return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    
    elif method == 'zscore':
        z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
        return df[z_scores <= threshold]
    
    else:
        raise ValueError("Method must be 'iqr' or 'zscore'")

def fill_missing_values(df: pd.DataFrame, column: str, method: str = 'linear') -> pd.DataFrame:
    """
    Fill missing values in a column
    """
    if method == 'linear':
        df[column] = df[column].interpolate(method='linear')
    elif method == 'mean':
        df[column] = df[column].fillna(df[column].mean())
    elif method == 'median':
        df[column] = df[column].fillna(df[column].median())
    elif method == 'ffill':
        df[column] = df[column].fillna(method='ffill')
    elif method == 'bfill':
        df[column] = df[column].fillna(method='bfill')
    else:
        raise ValueError("Method must be 'linear', 'mean', 'median', 'ffill', or 'bfill'")
    
    return df

# Data transformation functions
def resample_time_series(df: pd.DataFrame, date_column: str, value_column: str, 
                         freq: str = 'M', agg_func: str = 'mean') -> pd.DataFrame:
    """
    Resample time series data to a different frequency
    
    Args:
        df: DataFrame with time series data
        date_column: Name of the date column
        value_column: Name of the value column
        freq: Frequency string (D=day, W=week, M=month, Y=year)
        agg_func: Aggregation function (mean, sum, min, max)
    
    Returns:
        Resampled DataFrame
    """
    # Make sure date column is datetime
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Set date as index
    df_copy = df.copy()
    df_copy.set_index(date_column, inplace=True)
    
    # Resample
    if agg_func == 'mean':
        resampled = df_copy[[value_column]].resample(freq).mean()
    elif agg_func == 'sum':
        resampled = df_copy[[value_column]].resample(freq).sum()
    elif agg_func == 'min':
        resampled = df_copy[[value_column]].resample(freq).min()
    elif agg_func == 'max':
        resampled = df_copy[[value_column]].resample(freq).max()
    else:
        raise ValueError("agg_func must be 'mean', 'sum', 'min', or 'max'")
    
    # Reset index
    resampled.reset_index(inplace=True)
    
    return resampled

def calculate_anomalies(df: pd.DataFrame, date_column: str, value_column: str, 
                       baseline_start: Optional[str] = None, baseline_end: Optional[str] = None) -> pd.DataFrame:
    """
    Calculate anomalies relative to a baseline period or long-term averages
    
    Args:
        df: DataFrame with time series data
        date_column: Name of the date column
        value_column: Name of the value column
        baseline_start: Start date of baseline period (optional)
        baseline_end: End date of baseline period (optional)
    
    Returns:
        DataFrame with original data and anomalies
    """
    # Make sure date column is datetime
    df[date_column] = pd.to_datetime(df[date_column])
    
    # Create a copy of the dataframe
    result = df.copy()
    
    # Extract month for seasonal cycle
    result['month'] = result[date_column].dt.month
    
    # Calculate baseline averages for each month
    if baseline_start and baseline_end:
        baseline = result[(result[date_column] >= baseline_start) & 
                         (result[date_column] <= baseline_end)]
        monthly_means = baseline.groupby('month')[value_column].mean().reset_index()
    else:
        monthly_means = result.groupby('month')[value_column].mean().reset_index()
    
    monthly_means.columns = ['month', 'baseline_mean']
    
    # Merge with original data
    result = pd.merge(result, monthly_means, on='month')
    
    # Calculate anomalies
    result[f'{value_column}_anomaly'] = result[value_column] - result['baseline_mean']
    
    return result

# Visualization functions
def create_time_series_plot(df: pd.DataFrame, date_column: str, value_column: str, 
                          title: str = 'Time Series Plot', 
                          color: str = 'blue', 
                          fig_size: Tuple[int, int] = (10, 6)) -> str:
    """
    Create a time series plot and return as base64 encoded image
    """
    plt.figure(figsize=fig_size)
    plt.plot(df[date_column], df[value_column], color=color)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(value_column)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Save plot to a bytes buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    # Encode the image to base64
    img_str = base64.b64encode(buf.read()).decode()
    plt.close()
    
    return img_str

def create_folium_map(df: pd.DataFrame, lat_column: str, lon_column: str, 
                   value_column: Optional[str] = None, 
                   map_type: str = 'marker') -> folium.Map:
    """
    Create a Folium map from geospatial data
    
    Args:
        df: DataFrame with geospatial data
        lat_column: Name of the latitude column
        lon_column: Name of the longitude column
        value_column: Name of the value column (for choropleth or heatmap)
        map_type: Type of map ('marker', 'heatmap', 'choropleth')
    
    Returns:
        Folium Map object
    """
    # Calculate the center of the map
    center_lat = df[lat_column].mean()
    center_lon = df[lon_column].mean()
    
    # Create map
    m = folium.Map(location=[center_lat, center_lon], zoom_start=5)
    
    if map_type == 'marker':
        # Add markers
        for idx, row in df.iterrows():
            popup_text = "<br>".join([f"{col}: {row[col]}" for col in df.columns])
            folium.Marker(
                [row[lat_column], row[lon_column]],
                popup=folium.Popup(popup_text, max_width=300)
            ).add_to(m)
    
    elif map_type == 'heatmap' and value_column:
        # Add heatmap
        from folium.plugins import HeatMap
        heat_data = [[row[lat_column], row[lon_column], row[value_column]] for idx, row in df.iterrows()]
        HeatMap(heat_data).add_to(m)
    
    elif map_type == 'choropleth' and value_column:
        # This would require GeoJSON data, which is more complex to implement
        # For simplicity, fallback to marker map
        for idx, row in df.iterrows():
            popup_text = "<br>".join([f"{col}: {row[col]}" for col in df.columns])
            folium.Marker(
                [row[lat_column], row[lon_column]],
                popup=folium.Popup(popup_text, max_width=300)
            ).add_to(m)
    
    return m

# Export functions
def export_to_csv(df: pd.DataFrame) -> str:
    """
    Export DataFrame to CSV string
    """
    return df.to_csv(index=False)

def export_to_geojson(df: pd.DataFrame, lat_column: str, lon_column: str, 
                    properties: Optional[List[str]] = None) -> str:
    """
    Export DataFrame to GeoJSON string
    
    Args:
        df: DataFrame with geospatial data
        lat_column: Name of the latitude column
        lon_column: Name of the longitude column
        properties: List of columns to include as properties
    
    Returns:
        GeoJSON string
    """
    features = []
    
    if properties is None:
        properties = [col for col in df.columns if col not in [lat_column, lon_column]]
    
    for idx, row in df.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row[lon_column]), float(row[lat_column])]
            },
            "properties": {prop: row[prop] for prop in properties if prop in row}
        }
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    
    return json.dumps(geojson)
