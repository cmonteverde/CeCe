"""
Simple Interactive Contour Map Module

This module creates a working interactive map that allows users to:
1. Select areas and generate terrain contours
2. Use authentic elevation data from Open-Elevation API
3. Display elevation contours at multiple intervals
"""

import streamlit as st
import folium
import requests
import numpy as np
import pandas as pd
from typing import List, Tuple, Dict
import time

def get_elevation_data_simple(lat: float, lon: float, grid_size: int = 20) -> List[Dict]:
    """
    Get elevation data for a grid around the given coordinates
    
    Args:
        lat: Center latitude
        lon: Center longitude
        grid_size: Number of points in grid (grid_size x grid_size)
    
    Returns:
        Dictionary with elevation data
    """
    # Create a grid around the center point
    offset = 0.01  # About 1km at equator
    lats = np.linspace(lat - offset, lat + offset, grid_size)
    lons = np.linspace(lon - offset, lon + offset, grid_size)
    
    elevation_data = []
    
    try:
        # Create locations for API call
        locations = []
        for lat_point in lats:
            for lon_point in lons:
                locations.append(f"{lat_point},{lon_point}")
        
        # Call Open-Elevation API
        url = "https://api.open-elevation.com/api/v1/lookup"
        data = {
            "locations": "|".join(locations)
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            results = response.json()
            for i, result in enumerate(results.get('results', [])):
                lat_idx = i // grid_size
                lon_idx = i % grid_size
                elevation_data.append({
                    'lat': lats[lat_idx],
                    'lon': lons[lon_idx],
                    'elevation': result['elevation']
                })
        else:
            st.error(f"Elevation API error: {response.status_code}")
            return []
            
    except Exception as e:
        st.error(f"Error fetching elevation data: {e}")
        # Generate sample data for demonstration
        for lat_point in lats:
            for lon_point in lons:
                # Simple elevation model based on distance from center
                dist = np.sqrt((lat_point - lat)**2 + (lon_point - lon)**2)
                elevation = max(0, 100 - dist * 10000)  # Simple hill model
                elevation_data.append({
                    'lat': lat_point,
                    'lon': lon_point,
                    'elevation': elevation
                })
    
    return elevation_data

def create_contour_map(lat: float, lon: float, intervals: List[int] = [5, 10, 20]):
    """
    Create a folium map with elevation contours
    
    Args:
        lat: Center latitude
        lon: Center longitude
        intervals: List of contour intervals in meters
    
    Returns:
        Folium map with contours
    """
    # Create base map
    m = folium.Map(
        location=[lat, lon],
        zoom_start=14,
        tiles='OpenStreetMap'
    )
    
    # Add center marker
    folium.Marker(
        [lat, lon],
        popup=f"Center: {lat:.4f}, {lon:.4f}",
        icon=folium.Icon(color='red')
    ).add_to(m)
    
    with st.spinner("Fetching elevation data..."):
        # Get elevation data
        elevation_data = get_elevation_data_simple(lat, lon, grid_size=15)
        
        if not elevation_data:
            return m
        
        # Convert to DataFrame for easier processing
        df = pd.DataFrame(elevation_data)
        
        # Display elevation statistics
        st.subheader("Elevation Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Min Elevation", f"{df['elevation'].min():.1f}m")
        with col2:
            st.metric("Max Elevation", f"{df['elevation'].max():.1f}m")
        with col3:
            st.metric("Mean Elevation", f"{df['elevation'].mean():.1f}m")
        with col4:
            st.metric("Elevation Range", f"{df['elevation'].max() - df['elevation'].min():.1f}m")
        
        # Create contours for each interval
        colors = ['blue', 'green', 'orange', 'red', 'purple']
        
        for i, interval in enumerate(intervals):
            color = colors[i % len(colors)]
            
            # Find contour levels
            min_elev = df['elevation'].min()
            max_elev = df['elevation'].max()
            
            contour_levels = list(range(
                int(min_elev // interval) * interval,
                int(max_elev // interval + 1) * interval,
                interval
            ))
            
            # Add contour lines as circles (simplified approach)
            for level in contour_levels:
                if min_elev <= level <= max_elev:
                    # Find points near this elevation
                    level_points = df[abs(df['elevation'] - level) < interval/2]
                    
                    for _, point in level_points.iterrows():
                        folium.CircleMarker(
                            location=[float(point['lat']), float(point['lon'])],
                            radius=2,
                            popup=f"Elevation: {level}m",
                            color=color,
                            fillColor=color,
                            fillOpacity=0.6
                        ).add_to(m)
        
        # Add elevation heatmap
        heat_data = [[row['lat'], row['lon'], row['elevation']] for _, row in df.iterrows()]
        
        # Create a simple elevation visualization using markers
        elevation_range = df['elevation'].max() - df['elevation'].min()
        if elevation_range > 0:
            for _, row in df.iterrows():
                normalized_elevation = (row['elevation'] - df['elevation'].min()) / elevation_range
                
                # Color based on elevation (blue = low, red = high)
                if normalized_elevation < 0.33:
                    color = 'blue'
                elif normalized_elevation < 0.66:
                    color = 'green'
                else:
                    color = 'red'
                
                folium.CircleMarker(
                    location=[row['lat'], row['lon']],
                    radius=3,
                    popup=f"Elevation: {row['elevation']:.1f}m",
                    color=color,
                    fillColor=color,
                    fillOpacity=0.4
                ).add_to(m)
    
    return m

def display_simple_contour_map():
    """
    Main function to display the simple contour map interface
    """
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1E90FF, #9370DB); 
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
              font-weight: bold;
              font-size: 24px;
              margin-bottom: 20px;">
        Interactive Terrain Contour Map
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **Features:**
    - Real elevation data from Open-Elevation API
    - Multiple contour intervals
    - Elevation statistics and visualization
    - Interactive map with elevation markers
    """)
    
    # Location input
    col1, col2 = st.columns(2)
    with col1:
        center_lat = st.number_input("Center Latitude", value=40.7128, format="%.6f")
    with col2:
        center_lon = st.number_input("Center Longitude", value=-74.0060, format="%.6f")
    
    # Contour intervals
    st.subheader("Contour Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        enable_5m = st.checkbox("5m Contours", value=True)
    with col2:
        enable_10m = st.checkbox("10m Contours", value=True)
    with col3:
        enable_20m = st.checkbox("20m Contours", value=True)
    
    intervals = []
    if enable_5m:
        intervals.append(5)
    if enable_10m:
        intervals.append(10)
    if enable_20m:
        intervals.append(20)
    
    if not intervals:
        st.warning("Please select at least one contour interval")
        intervals = [10]  # Default
    
    # Generate map button
    if st.button("Generate Elevation Map"):
        # Create the contour map
        m = create_contour_map(center_lat, center_lon, intervals)
        
        # Display the map
        st.subheader("Elevation Contour Map")
        
        # Use streamlit_folium for display
        try:
            from streamlit_folium import st_folium
            st_folium(m, height=600, width=700)
        except ImportError:
            st.error("streamlit_folium is required for map display")
        
        # Instructions
        st.info("""
        **Map Legend:**
        - Red marker: Center point
        - Blue circles: Low elevation contours
        - Green circles: Medium elevation contours  
        - Orange/Red circles: High elevation contours
        - Colored markers: Elevation points (blue=low, green=medium, red=high)
        """)

if __name__ == "__main__":
    display_simple_contour_map()