import os
import pandas as pd
import requests
import numpy as np
import tempfile
import urllib.parse
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, timedelta
import io
# Temporarily disable langchain imports
# from langchain.document_loaders import (
#     DataFrameLoader,
#     CSVLoader,
#     TextLoader,
#     JSONLoader
# )
# from langchain.document_loaders.excel import UnstructuredExcelLoader
# from langchain.schema import Document
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# NASA POWER API client
def load_nasa_power_data(
    lat: float, 
    lon: float, 
    start_date: str, 
    end_date: str, 
    parameters: List[str] = None
) -> pd.DataFrame:
    """
    Load climate data from NASA POWER API
    
    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        start_date: Start date in format 'YYYYMMDD'
        end_date: End date in format 'YYYYMMDD'
        parameters: List of parameters to fetch
    
    Returns:
        DataFrame with climate data
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
        response.raise_for_status()
        
        data = response.json()
        
        # Extract the data
        if "properties" in data and "parameter" in data["properties"]:
            parameter_data = data["properties"]["parameter"]
            
            # Create DataFrame
            df = pd.DataFrame()
            
            # Get the dates
            dates = list(parameter_data[parameters[0]].keys())
            df["DATE"] = [datetime.strptime(date, "%Y%m%d") for date in dates]
            
            # Add each parameter
            for param in parameters:
                if param in parameter_data:
                    df[param] = [parameter_data[param][date] for date in dates]
            
            return df
        else:
            raise ValueError("Unexpected API response format")
    
    except Exception as e:
        raise Exception(f"Error fetching NASA POWER data: {str(e)}")

# Load CSV file
def load_csv_file(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Load a CSV file into a DataFrame
    
    Args:
        file_path: Path to CSV file
        **kwargs: Additional arguments to pass to pd.read_csv()
    
    Returns:
        DataFrame with data from CSV file
    """
    try:
        df = pd.read_csv(file_path, **kwargs)
        return df
    except Exception as e:
        raise Exception(f"Error loading CSV file: {str(e)}")

# Load Excel file
def load_excel_file(file_path: str, sheet_name=0, **kwargs) -> pd.DataFrame:
    """
    Load an Excel file into a DataFrame
    
    Args:
        file_path: Path to Excel file
        sheet_name: Sheet name or index
        **kwargs: Additional arguments to pass to pd.read_excel()
    
    Returns:
        DataFrame with data from Excel file
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, **kwargs)
        return df
    except Exception as e:
        raise Exception(f"Error loading Excel file: {str(e)}")

# Load JSON file
def load_json_file(file_path: str, **kwargs) -> pd.DataFrame:
    """
    Load a JSON file into a DataFrame
    
    Args:
        file_path: Path to JSON file
        **kwargs: Additional arguments to pass to pd.read_json()
    
    Returns:
        DataFrame with data from JSON file
    """
    try:
        df = pd.read_json(file_path, **kwargs)
        return df
    except Exception as e:
        raise Exception(f"Error loading JSON file: {str(e)}")

# Load data from uploaded file (Streamlit)
def load_uploaded_file(uploaded_file) -> pd.DataFrame:
    """
    Load an uploaded file into a DataFrame
    
    Args:
        uploaded_file: Streamlit uploaded file object
    
    Returns:
        DataFrame with data from uploaded file
    """
    try:
        # Check file extension
        file_extension = os.path.splitext(uploaded_file.name)[1].lower()
        
        if file_extension == '.csv':
            df = pd.read_csv(uploaded_file)
        elif file_extension in ['.xls', '.xlsx']:
            df = pd.read_excel(uploaded_file)
        elif file_extension == '.json':
            df = pd.read_json(uploaded_file)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
        
        return df
    
    except Exception as e:
        raise Exception(f"Error loading uploaded file: {str(e)}")

# Load documents from DataFrame for RAG (temporarily disabled)
def load_documents_from_dataframe(df: pd.DataFrame, metadata: Optional[Dict[str, Any]] = None) -> List:
    """
    Load documents from a DataFrame for RAG
    
    Args:
        df: Pandas DataFrame
        metadata: Additional metadata to add to documents
    
    Returns:
        List of Document objects (currently just returns empty list)
    """
    # This function is temporarily disabled until langchain is available
    return []

# Generate synthetic climate data for testing
def generate_synthetic_climate_data(
    start_date: str, 
    end_date: str, 
    location_name: str = "Sample Location",
    lat: float = 40.0,
    lon: float = -75.0
) -> pd.DataFrame:
    """
    Generate synthetic climate data for testing
    
    Args:
        start_date: Start date in format 'YYYY-MM-DD'
        end_date: End date in format 'YYYY-MM-DD'
        location_name: Name of the location
        lat: Latitude
        lon: Longitude
    
    Returns:
        DataFrame with synthetic climate data
    """
    # Convert dates to datetime
    start = pd.to_datetime(start_date)
    end = pd.to_datetime(end_date)
    
    # Create date range
    date_range = pd.date_range(start=start, end=end, freq='D')
    
    # Create DataFrame
    df = pd.DataFrame({'DATE': date_range})
    
    # Add day of year for seasonal patterns
    df['DAY_OF_YEAR'] = df['DATE'].dt.dayofyear
    
    # Generate temperature data with seasonal pattern
    # Base temperature curve: T = base_temp + amplitude * sin(2π * (day-offset)/365)
    base_temp = 15.0  # Base temperature in °C
    amplitude = 15.0  # Annual temperature amplitude
    phase_shift = 20  # Shift the peak to summer (day ~200)
    
    # Add some randomness to daily temperatures
    np.random.seed(42)  # For reproducibility
    daily_noise = np.random.normal(0, 3, len(df))  # Daily noise with 3°C standard deviation
    
    # Calculate mean daily temperature
    df['T2M'] = base_temp + amplitude * np.sin(2 * np.pi * (df['DAY_OF_YEAR'] - phase_shift) / 365) + daily_noise
    
    # Generate min and max temperatures (mean ± random variation)
    daily_range = 5.0 + np.random.normal(0, 1, len(df))  # Daily temperature range with some variation
    df['T2M_MIN'] = df['T2M'] - daily_range / 2 + np.random.normal(0, 1, len(df))
    df['T2M_MAX'] = df['T2M'] + daily_range / 2 + np.random.normal(0, 1, len(df))
    
    # Generate precipitation with seasonal patterns and random events
    # More rain in spring/fall, less in summer/winter
    precip_pattern = 2 + 3 * np.sin(4 * np.pi * (df['DAY_OF_YEAR'] - 80) / 365)  # Bimodal pattern
    
    # Generate random precipitation events
    rain_prob = precip_pattern / 10  # Probability of rain each day
    rain_events = np.random.random(len(df)) < rain_prob
    
    # Rain amount follows a gamma distribution
    rain_amount = np.random.gamma(shape=1.5, scale=5, size=len(df)) * rain_events
    df['PRECTOT'] = rain_amount
    
    # Generate relative humidity (related to temperature and precipitation)
    base_humidity = 70.0  # Base humidity level
    temp_effect = -0.5 * (df['T2M'] - base_temp)  # Higher temps -> lower humidity
    precip_effect = 10 * (rain_events)  # Rain -> higher humidity
    
    df['RH2M'] = base_humidity + temp_effect + precip_effect + np.random.normal(0, 5, len(df))
    df['RH2M'] = df['RH2M'].clip(10, 100)  # Clip to valid range
    
    # Generate wind speed
    df['WS2M'] = 3.0 + np.random.gamma(shape=1.2, scale=1.5, size=len(df))
    
    # Add location information
    df['LOCATION'] = location_name
    df['LAT'] = lat
    df['LON'] = lon
    
    # Clean up
    df = df.drop('DAY_OF_YEAR', axis=1)
    
    return df
