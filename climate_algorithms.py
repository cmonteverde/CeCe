import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union

# Temperature unit conversion functions
def celsius_to_fahrenheit(celsius: float) -> float:
    """
    Convert temperature from Celsius to Fahrenheit
    """
    return (celsius * 9/5) + 32

def fahrenheit_to_celsius(fahrenheit: float) -> float:
    """
    Convert temperature from Fahrenheit to Celsius
    """
    return (fahrenheit - 32) * 5/9

# Growing Degree Day (GDD) calculation
def calculate_gdd(tmax: float, tmin: float, base_temp: float = 10.0, 
                 upper_threshold: Optional[float] = None, 
                 method: str = 'average') -> float:
    """
    Calculate Growing Degree Days (GDD)
    
    Args:
        tmax: Maximum temperature (°C)
        tmin: Minimum temperature (°C)
        base_temp: Base temperature (°C)
        upper_threshold: Upper temperature threshold (°C)
        method: Calculation method ('average', 'modified')
    
    Returns:
        GDD value
    """
    if method == 'average':
        # Standard method: (Tmax + Tmin) / 2 - Tbase
        if upper_threshold:
            tmax = min(tmax, upper_threshold)
        tavg = (tmax + tmin) / 2
        gdd = max(0, tavg - base_temp)
    
    elif method == 'modified':
        # Modified method: adjust Tmin if below base temp
        if upper_threshold:
            tmax = min(tmax, upper_threshold)
        tmin = max(tmin, base_temp)
        tavg = (tmax + tmin) / 2
        gdd = max(0, tavg - base_temp)
    
    else:
        raise ValueError("Method must be 'average' or 'modified'")
    
    return gdd

# Accumulated GDD calculation
def calculate_accumulated_gdd(temps_df: pd.DataFrame, tmax_col: str, tmin_col: str, 
                             date_col: str, base_temp: float = 10.0,
                             upper_threshold: Optional[float] = None, 
                             method: str = 'average') -> pd.DataFrame:
    """
    Calculate accumulated GDD over a time period
    
    Args:
        temps_df: DataFrame with temperature data
        tmax_col: Column name for maximum temperature
        tmin_col: Column name for minimum temperature
        date_col: Column name for date
        base_temp: Base temperature (°C)
        upper_threshold: Upper temperature threshold (°C)
        method: Calculation method ('average', 'modified')
    
    Returns:
        DataFrame with date, daily GDD, and accumulated GDD
    """
    # Sort by date
    temps_df = temps_df.sort_values(by=date_col)
    
    # Calculate daily GDD
    temps_df['daily_gdd'] = temps_df.apply(
        lambda row: calculate_gdd(
            row[tmax_col], row[tmin_col], 
            base_temp=base_temp, 
            upper_threshold=upper_threshold,
            method=method
        ), 
        axis=1
    )
    
    # Calculate accumulated GDD
    temps_df['accumulated_gdd'] = temps_df['daily_gdd'].cumsum()
    
    return temps_df

# Potential Evapotranspiration (PET) calculation - Hargreaves method
def calculate_pet_hargreaves(tmax: float, tmin: float, tmean: float, 
                            lat_rad: float, day_of_year: int) -> float:
    """
    Calculate Potential Evapotranspiration using Hargreaves method
    
    Args:
        tmax: Maximum temperature (°C)
        tmin: Minimum temperature (°C)
        tmean: Mean temperature (°C)
        lat_rad: Latitude in radians
        day_of_year: Day of year (1-366)
    
    Returns:
        Daily PET in mm/day
    """
    # Calculate extraterrestrial radiation (Ra)
    # Solar declination
    solar_dec = 0.409 * np.sin(2 * np.pi * day_of_year / 365 - 1.39)
    
    # Sunset hour angle
    sunset_angle = np.arccos(-np.tan(lat_rad) * np.tan(solar_dec))
    
    # Relative distance Earth-Sun
    dr = 1 + 0.033 * np.cos(2 * np.pi * day_of_year / 365)
    
    # Extraterrestrial radiation
    ra = 24 * 60 / np.pi * 0.0820 * dr * (
        sunset_angle * np.sin(lat_rad) * np.sin(solar_dec) + 
        np.cos(lat_rad) * np.cos(solar_dec) * np.sin(sunset_angle)
    )
    
    # Hargreaves PET equation
    pet = 0.0023 * ra * (tmean + 17.8) * np.sqrt(tmax - tmin)
    
    return pet

# Standardized Precipitation Index (SPI)
def calculate_spi(rainfall_data: pd.Series, scale: int = 3) -> pd.Series:
    """
    Calculate Standardized Precipitation Index (SPI)
    
    Args:
        rainfall_data: Series of monthly rainfall data
        scale: Number of months for the moving window
    
    Returns:
        Series of SPI values
    """
    if len(rainfall_data) < scale * 2:
        raise ValueError(f"Need at least {scale * 2} data points to calculate SPI at scale {scale}")
    
    # Calculate rolling sum for the given scale
    rolling_sum = rainfall_data.rolling(window=scale, min_periods=scale).sum()
    
    # Calculate mean and standard deviation
    mean = rolling_sum.mean()
    std = rolling_sum.std()
    
    # Calculate SPI (z-score)
    spi = (rolling_sum - mean) / std
    
    return spi

# Heat Index calculation
def calculate_heat_index(temperature: float, relative_humidity: float) -> float:
    """
    Calculate Heat Index based on temperature and relative humidity
    
    Args:
        temperature: Temperature in Celsius
        relative_humidity: Relative humidity (%)
    
    Returns:
        Heat Index in Celsius
    """
    # Convert temperature to Fahrenheit for the standard formula
    tf = celsius_to_fahrenheit(temperature)
    rh = relative_humidity
    
    # Simplified heat index formula
    hi = 0.5 * (tf + 61.0 + ((tf - 68.0) * 1.2) + (rh * 0.094))
    
    # If temperature and humidity are high enough, use the full formula
    if tf >= 80.0 and rh >= 40.0:
        hi = -42.379 + 2.04901523 * tf + 10.14333127 * rh \
             - 0.22475541 * tf * rh - 6.83783e-3 * tf**2 \
             - 5.481717e-2 * rh**2 + 1.22874e-3 * tf**2 * rh \
             + 8.5282e-4 * tf * rh**2 - 1.99e-6 * tf**2 * rh**2
    
    # Convert back to Celsius
    hi_celsius = fahrenheit_to_celsius(hi)
    
    return hi_celsius

# Wind Chill calculation
def calculate_wind_chill(temperature: float, wind_speed: float) -> float:
    """
    Calculate Wind Chill factor based on temperature and wind speed
    
    Args:
        temperature: Temperature in Celsius
        wind_speed: Wind speed in m/s
    
    Returns:
        Wind Chill temperature in Celsius
    """
    # Wind chill is only defined for temperatures at or below 10°C (50°F)
    # and wind speeds above 1.3 m/s (3 mph)
    if temperature > 10 or wind_speed <= 1.3:
        return temperature
    
    # Convert wind speed from m/s to km/h
    wind_speed_kmh = wind_speed * 3.6
    
    # Calculate wind chill using the new Wind Chill index formula
    wind_chill = 13.12 + 0.6215 * temperature - 11.37 * wind_speed_kmh**0.16 + 0.3965 * temperature * wind_speed_kmh**0.16
    
    return wind_chill

# Identify extreme temperature days
def identify_extreme_heat_days(temps_df: pd.DataFrame, temp_col: str, date_col: str, 
                             threshold_percentile: float = 95.0) -> pd.DataFrame:
    """
    Identify extreme heat days based on a percentile threshold
    
    Args:
        temps_df: DataFrame with temperature data
        temp_col: Column name for temperature
        date_col: Column name for date
        threshold_percentile: Percentile threshold for extreme heat (default: 95%)
    
    Returns:
        DataFrame with filtered extreme heat days
    """
    # Calculate the threshold temperature
    threshold_temp = temps_df[temp_col].quantile(threshold_percentile / 100)
    
    # Filter the dataframe to include only extreme heat days
    extreme_days = temps_df[temps_df[temp_col] >= threshold_temp].copy()
    
    # Add a column indicating how much above the threshold
    extreme_days['degrees_above_threshold'] = extreme_days[temp_col] - threshold_temp
    
    return extreme_days

# Climate Comfort Index
def calculate_comfort_index(temperature: float, relative_humidity: float, 
                          wind_speed: float = 0) -> Tuple[float, str]:
    """
    Calculate a simple thermal comfort index
    
    Args:
        temperature: Temperature in Celsius
        relative_humidity: Relative humidity (%)
        wind_speed: Wind speed in m/s
    
    Returns:
        Tuple of (comfort_index, comfort_category)
    """
    # Base discomfort on temperature
    if temperature < 5:
        base_discomfort = 10 - temperature  # Cold discomfort
    elif temperature > 25:
        base_discomfort = temperature - 25  # Heat discomfort
    else:
        base_discomfort = 0  # Comfortable temperature range
    
    # Adjust for humidity
    humidity_factor = 0
    if temperature > 20:
        # High humidity makes hot weather feel worse
        humidity_factor = (relative_humidity - 50) / 5 if relative_humidity > 50 else 0
    
    # Adjust for wind - wind makes cold weather feel colder and hot weather feel better
    wind_factor = 0
    if temperature < 10:
        wind_factor = wind_speed / 2  # Wind makes cold worse
    elif temperature > 25:
        wind_factor = -wind_speed / 4  # Wind makes heat more bearable
    
    # Calculate comfort index (0 = comfortable, higher = more uncomfortable)
    comfort_index = base_discomfort + humidity_factor + wind_factor
    
    # Determine comfort category
    if comfort_index < 2:
        comfort_category = "Very Comfortable"
    elif comfort_index < 5:
        comfort_category = "Comfortable"
    elif comfort_index < 10:
        comfort_category = "Slightly Uncomfortable"
    elif comfort_index < 15:
        comfort_category = "Uncomfortable"
    else:
        comfort_category = "Very Uncomfortable"
    
    return comfort_index, comfort_category

# Drought Index - Standardized Precipitation Evapotranspiration Index (SPEI)
def calculate_spei(precipitation: pd.Series, pet: pd.Series, scale: int = 3) -> pd.Series:
    """
    Calculate Standardized Precipitation Evapotranspiration Index (SPEI)
    
    Args:
        precipitation: Series of monthly precipitation data
        pet: Series of monthly potential evapotranspiration data
        scale: Number of months for the moving window
    
    Returns:
        Series of SPEI values
    """
    # Calculate climatic water balance
    water_balance = precipitation - pet
    
    # Calculate SPEI (similar to SPI but using water balance instead of just precipitation)
    spei = calculate_spi(water_balance, scale)
    
    return spei

# Frost Risk Assessment
def calculate_frost_risk(tmin: float, dewpoint: float = None, 
                        month: int = None, latitude: float = None) -> str:
    """
    Calculate frost risk based on minimum temperature and other factors
    
    Args:
        tmin: Minimum temperature (°C)
        dewpoint: Dewpoint temperature (°C)
        month: Month of the year (1-12)
        latitude: Latitude (degrees)
    
    Returns:
        Frost risk category
    """
    # Base risk on minimum temperature
    if tmin > 4:
        risk = "No Risk"
    elif tmin > 0:
        risk = "Low Risk"
    elif tmin > -3:
        risk = "Medium Risk"
    else:
        risk = "High Risk"
    
    # If we have dewpoint, adjust risk (closer dewpoint to tmin = higher risk)
    if dewpoint is not None:
        dewpoint_diff = tmin - dewpoint
        if dewpoint_diff < 2 and tmin <= 4:
            # Increase risk one level if dewpoint is close to min temp
            if risk == "No Risk":
                risk = "Low Risk"
            elif risk == "Low Risk":
                risk = "Medium Risk"
            elif risk == "Medium Risk":
                risk = "High Risk"
    
    # Adjust risk based on month and latitude (if provided)
    # (This is a simplified adjustment - real models would be more complex)
    if month is not None and latitude is not None:
        # Northern hemisphere seasonal adjustment
        if latitude > 0:
            # Higher risk in spring months at higher latitudes
            if month in [3, 4, 5] and latitude > 40 and tmin <= 4:
                if risk == "No Risk":
                    risk = "Low Risk"
                elif risk == "Low Risk":
                    risk = "Medium Risk"
                elif risk == "Medium Risk":
                    risk = "High Risk"
        # Southern hemisphere seasonal adjustment
        else:
            # Higher risk in southern hemisphere spring (Sep-Nov)
            if month in [9, 10, 11] and latitude < -40 and tmin <= 4:
                if risk == "No Risk":
                    risk = "Low Risk"
                elif risk == "Low Risk":
                    risk = "Medium Risk"
                elif risk == "Medium Risk":
                    risk = "High Risk"
    
    return risk

# Fire Weather Index (simplified version)
def calculate_fire_weather_index(temperature: float, relative_humidity: float, 
                               wind_speed: float, precipitation: float) -> Tuple[float, str]:
    """
    Calculate a simplified Fire Weather Index
    
    Args:
        temperature: Temperature in Celsius
        relative_humidity: Relative humidity (%)
        wind_speed: Wind speed in m/s
        precipitation: Precipitation amount in mm
    
    Returns:
        Tuple of (fwi_value, risk_category)
    """
    # Temperature factor (higher temp = higher risk)
    temp_factor = max(0, (temperature - 10) / 30)
    
    # Humidity factor (lower humidity = higher risk)
    humidity_factor = max(0, (100 - relative_humidity) / 100)
    
    # Wind factor (higher wind = higher risk)
    wind_factor = min(1, wind_speed / 40)
    
    # Precipitation factor (more rain = lower risk)
    precip_factor = max(0, 1 - (precipitation / 10))
    
    # Calculate simplified FWI (0 = low risk, 1 = extreme risk)
    fwi = (0.3 * temp_factor + 0.4 * humidity_factor + 0.3 * wind_factor) * precip_factor
    
    # Determine risk category
    if fwi < 0.2:
        risk_category = "Low"
    elif fwi < 0.4:
        risk_category = "Moderate"
    elif fwi < 0.6:
        risk_category = "High"
    elif fwi < 0.8:
        risk_category = "Very High"
    else:
        risk_category = "Extreme"
    
    return fwi, risk_category
