"""
Felt-Inspired Map Demo for Climate Copilot

This module demonstrates the Felt-inspired map capabilities 
with modern styling and interactive climate data overlays.
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import folium_static
import random
import json
import os
import io
import matplotlib.pyplot as plt

# Import our custom map module
import felt_inspired_maps

def run_felt_map_demo():
    """Main function to run the Felt-inspired map demo in Streamlit"""
    
    st.title("Climate Copilot: Felt-Inspired Maps")
    
    # Sidebar for map controls
    with st.sidebar:
        st.header("Map Settings")
        
        # Location selection
        st.subheader("Location")
        location_options = {
            "San Francisco": (37.7749, -122.4194),
            "New York": (40.7128, -74.0060),
            "Chicago": (41.8781, -87.6298),
            "Denver": (39.7392, -104.9903),
            "Seattle": (47.6062, -122.3321),
            "Miami": (25.7617, -80.1918),
            "Custom": (0, 0)
        }
        
        selected_location = st.selectbox("Select location", options=list(location_options.keys()))
        
        if selected_location == "Custom":
            col1, col2 = st.columns(2)
            lat = col1.number_input("Latitude", value=0.0, min_value=-90.0, max_value=90.0, format="%.4f")
            lon = col2.number_input("Longitude", value=0.0, min_value=-180.0, max_value=180.0, format="%.4f")
        else:
            lat, lon = location_options[selected_location]
        
        # Map appearance
        st.subheader("Appearance")
        basemap = st.selectbox(
            "Base map style",
            options=[
                "light", "dark", "outdoors", "satellite", 
                "terrain", "hybrid", "topo", "street", "watercolor"
            ],
            index=0
        )
        
        ui_style = st.selectbox(
            "UI Style",
            options=["modern", "minimal", "detailed"],
            index=0
        )
        
        zoom_level = st.slider("Zoom level", min_value=3, max_value=15, value=10)
        
        # Layer toggles
        st.subheader("Map Layers")
        show_contours = st.checkbox("Elevation Contours", value=True)
        contour_color = st.color_picker("Contour Color", "#6644aa")
        
        show_temperature = st.checkbox("Temperature Layer", value=False)
        show_precipitation = st.checkbox("Precipitation Layer", value=False)
        show_wind = st.checkbox("Wind Patterns", value=False)
        show_risk = st.checkbox("Climate Risk Zones", value=False)
        
        st.subheader("Map Features")
        show_toolbar = st.checkbox("Show Toolbar", value=True)
        height = st.slider("Map Height", min_value=400, max_value=1000, value=600)
    
    # Main content area
    st.subheader(f"Interactive Climate Map: {selected_location}")
    
    # Create description based on enabled layers
    enabled_layers = []
    if show_contours:
        enabled_layers.append("elevation contours")
    if show_temperature:
        enabled_layers.append("temperature data")
    if show_precipitation:
        enabled_layers.append("precipitation patterns")
    if show_wind:
        enabled_layers.append("wind visualization")
    if show_risk:
        enabled_layers.append("climate risk zones")
    
    layer_text = ", ".join(enabled_layers)
    if layer_text:
        st.markdown(f"Map showing {layer_text} for the selected region.")
    else:
        st.markdown("Select layers from the sidebar to visualize climate data.")
    
    # Create the map
    felt_map = felt_inspired_maps.create_felt_inspired_map(
        lat=lat,
        lon=lon,
        zoom=zoom_level,
        width="100%",
        height=height,
        tiles=basemap,
        style=ui_style,
        show_toolbar=show_toolbar,
        include_contours=show_contours,
        contour_color=contour_color
    )
    
    # Add additional layers if requested
    if show_temperature:
        # Generate sample temperature data around the selected point
        temp_data = []
        grid_size = 10
        grid_spacing = 0.02  # Degrees
        
        for i in range(grid_size):
            for j in range(grid_size):
                grid_lat = lat + (i - grid_size/2) * grid_spacing
                grid_lon = lon + (j - grid_size/2) * grid_spacing
                
                # Create sample temperature with variation
                base_temp = 15.0  # Base temperature
                altitude_effect = random.uniform(-2.0, 2.0)  # Simulated altitude effect
                location_effect = random.uniform(-3.0, 3.0)  # Location variation
                
                temperature = base_temp + altitude_effect + location_effect
                
                temp_data.append((grid_lat, grid_lon, temperature))
        
        felt_map.add_temperature_layer(
            data=temp_data,
            min_temp=10.0,
            max_temp=25.0,
            radius=20,
            blur=15,
            name="Temperature Layer",
            palette="temperature"
        )
    
    if show_precipitation:
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
    
    if show_wind:
        # Generate sample wind data
        wind_data = []
        grid_size = 6
        grid_spacing = 0.03  # Degrees
        
        # Create a simple wind field
        for i in range(grid_size):
            for j in range(grid_size):
                grid_lat = lat + (i - grid_size/2) * grid_spacing
                grid_lon = lon + (j - grid_size/2) * grid_spacing
                
                # Create sample wind vectors (u,v) with a pattern
                u = 2.0 + random.uniform(-1.0, 1.0)  # Eastward component
                v = 1.0 + random.uniform(-1.0, 1.0)  # Northward component
                
                # Calculate wind speed
                speed = np.sqrt(u**2 + v**2)
                
                wind_data.append((grid_lat, grid_lon, u, v, speed))
        
        felt_map.add_wind_layer(
            wind_data=wind_data,
            name="Wind Patterns",
            palette="urban"
        )
    
    if show_risk:
        # Generate sample climate risk zones
        risk_data = []
        
        # Add a few sample risk areas
        risks = [
            ("high", "Flooding"),
            ("moderate", "Wildfire"),
            ("very high", "Drought"),
            ("low", "Sea Level Rise"),
            ("extreme", "Extreme Heat")
        ]
        
        for i, (risk_level, risk_type) in enumerate(risks):
            # Create a polygon around a point near the center
            offset_lat = random.uniform(-0.05, 0.05)
            offset_lon = random.uniform(-0.05, 0.05)
            
            center_lat = lat + offset_lat
            center_lon = lon + offset_lon
            
            # Create a simple circular polygon
            polygon_radius = 0.02 + random.uniform(0, 0.01)
            num_points = 20
            polygon_points = []
            
            for j in range(num_points):
                angle = 2 * np.pi * j / num_points
                pt_lat = center_lat + polygon_radius * np.sin(angle)
                pt_lon = center_lon + polygon_radius * np.cos(angle)
                polygon_points.append([pt_lon, pt_lat])
            
            # Close the polygon
            polygon_points.append(polygon_points[0])
            
            # Create GeoJSON
            geojson = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [polygon_points]
                },
                "properties": {
                    "risk_level": risk_level,
                    "risk_type": risk_type
                }
            }
            
            risk_data.append((center_lat, center_lon, geojson, risk_level, risk_type))
        
        felt_map.add_climate_risk_layer(
            risk_data=risk_data,
            name="Climate Risk Zones",
            palette="urban"
        )
    
    # Add points of interest
    poi_data = [
        (lat + 0.01, lon + 0.01, "Weather Station", "Primary regional weather monitoring station", "cloud", "blue"),
        (lat - 0.01, lon - 0.01, "Research Center", "Climate research and monitoring facility", "education", "green"),
        (lat + 0.02, lon - 0.02, "Flood Control", "Major flood control infrastructure", "tint", "red")
    ]
    
    felt_map.add_points_of_interest(poi_data, name="Climate Monitoring Sites", cluster=True)
    
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

    # Add technical notes
    st.caption("Map data © OpenStreetMap contributors | Climate visualization by Climate Copilot")

if __name__ == "__main__":
    run_felt_map_demo()