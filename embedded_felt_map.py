"""
Embedded Felt-Inspired Map for Climate Copilot

This module provides a simplified version of the Felt-inspired map
that can be embedded within other Streamlit applications.
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import random
import json
import os

# Import our custom map module
import felt_inspired_maps

def create_embedded_felt_map(lat, lon, location_name="Selected Location"):
    """Create a Felt-inspired map that can be embedded within another app
    
    Args:
        lat: Latitude
        lon: Longitude
        location_name: Name of the location
        
    Returns:
        None (displays the map in Streamlit)
    """
    # Create the map
    felt_map = felt_inspired_maps.create_felt_inspired_map(
        lat=lat,
        lon=lon,
        zoom=10,
        width="100%",
        height=600,
        tiles="dark",
        style="modern",
        show_toolbar=True,
        include_contours=True,
        contour_color="#6644aa"
    )
    
    # Generate sample precipitation data
    precip_data = []
    grid_size = 8
    grid_spacing = 0.025  # Degrees
    
    for i in range(grid_size):
        for j in range(grid_size):
            grid_lat = lat + (i - grid_size/2) * grid_spacing
            grid_lon = lon + (j - grid_size/2) * grid_spacing
            
            # Create sample precipitation with spatial correlation
            distance_from_center = np.sqrt((i - grid_size/2)**2 + (j - grid_size/2)**2)
            base_precip = max(0, 30 - distance_from_center * 5)  # More rain in center
            variation = random.uniform(-5.0, 10.0)
            
            precipitation = max(0, base_precip + variation)
            
            precip_data.append((grid_lat, grid_lon, precipitation))
    
    felt_map.add_precipitation_layer(
        data=precip_data,
        min_precip=0.0,
        max_precip=40.0,
        name="Precipitation Layer",
        palette="precipitation"
    )
    
    # Add points of interest
    poi_data = [
        (lat, lon, location_name, f"Coordinates: {lat:.4f}, {lon:.4f}", "map-pin", "purple")
    ]
    
    felt_map.add_points_of_interest(poi_data, name="Selected Location", cluster=False)
    
    # Display the map
    felt_map.render_in_streamlit()
    
    # Display information about the Felt-inspired map
    with st.expander("About Felt-Inspired Maps"):
        st.markdown("""
        ### Felt-Inspired Maps for Climate Data

        The Climate Copilot map system is inspired by [Felt](https://felt.com), a modern mapping platform 
        that emphasizes clean design, interactivity, and collaborative map creation. Our implementation 
        brings similar design principles to climate data visualization:

        - **Clean, modern UI** with minimalist controls and aesthetics
        - **Multiple high-quality basemaps** for different visualization needs
        - **Interactive data layers** with smooth transitions
        - **Enhanced data visualization** specifically for climate metrics
        - **Annotation capabilities** to highlight and explain climate phenomena

        These maps combine real elevation data with climate data overlays to provide
        comprehensive visualization of climate patterns and risks.
        """)