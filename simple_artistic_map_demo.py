"""
Simple Artistic Map Demo for Climate Copilot

This module demonstrates the artistic map capabilities
using a simplified approach that avoids complex image processing.
"""

import streamlit as st
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import folium_static
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import random

# Import our simplified artistic map module
import simple_artistic_maps

def run_artistic_map_demo():
    """
    Run the artistic map demonstration
    """
    st.markdown("<h2 style='text-align: center; color: #1E90FF;'>Artistic Climate Maps</h2>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: rgba(30, 30, 30, 0.6); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
        <p style="color: white;">
            Explore unique artistic map visualizations that combine climate science with visual artistry. 
            These maps use high-resolution topography, land use data, and satellite imagery to create
            distinctive visualizations that make climate data more engaging and memorable.
        </p>
        <p style="color: #add8e6; margin-top: 10px;">
            <strong>Interactive Features:</strong> Once generated, you can toggle between different basemaps, 
            turn topography lines on/off, and customize your view using the layer control panel in the top-right corner!
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Location selection
    st.markdown("<h3 style='color: #1E90FF;'>Select Location</h3>", unsafe_allow_html=True)
    
    location_method = st.radio(
        "How would you like to specify the location?",
        ("City Name", "Coordinates"),
        horizontal=True
    )
    
    if location_method == "City Name":
        city = st.text_input("Enter city name:", "Paris, France")
        try:
            # Use the existing function from the main app to get coordinates
            from app import get_city_coordinates
            
            # Try to get coordinates
            latitude, longitude = get_city_coordinates(city)
            
            # Check if we got valid coordinates
            if latitude is None or longitude is None:
                st.error(f"Could not find coordinates for '{city}'. Please try another city name or format like 'City, Country'.")
                # Set default coordinates for Paris to allow the demo to continue
                latitude, longitude = 48.8566, 2.3522
                st.warning(f"Using default coordinates for demonstration: {latitude:.4f}, {longitude:.4f}")
            else:
                st.success(f"Coordinates found: {latitude:.4f}, {longitude:.4f}")
        except Exception as e:
            st.error(f"Error getting coordinates: {str(e)}")
            # Set default coordinates to allow the demo to continue
            latitude, longitude = 48.8566, 2.3522
            st.warning(f"Using default coordinates for demonstration: {latitude:.4f}, {longitude:.4f}")
    else:
        col1, col2 = st.columns(2)
        with col1:
            latitude = st.number_input("Latitude:", value=48.8566, min_value=-90.0, max_value=90.0, step=0.01)
        with col2:
            longitude = st.number_input("Longitude:", value=2.3522, min_value=-180.0, max_value=180.0, step=0.01)
    
    # Map style selection
    st.markdown("<h3 style='color: #1E90FF;'>Map Style</h3>", unsafe_allow_html=True)
    
    map_style = st.selectbox(
        "Select artistic style:",
        ["ethereal", "dramatic", "moody", "surreal", "vibrant", "neon", "artistic"],
        index=0,
        format_func=lambda x: x.capitalize()
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        data_type = st.selectbox(
            "Data visualization type:",
            ["topography", "satellite"],
            index=0,
            format_func=lambda x: x.capitalize()
        )
    
    with col2:
        zoom_level = st.slider("Zoom level:", min_value=5, max_value=15, value=10)
    
    # Advanced options (collapsible)
    with st.expander("Advanced Options"):
        col1, col2 = st.columns(2)
        
        with col1:
            width = st.number_input("Map width (pixels):", value=800, min_value=400, max_value=1200, step=50)
        
        with col2:
            height = st.number_input("Map height (pixels):", value=600, min_value=300, max_value=900, step=50)
            
        custom_styling = st.checkbox("Apply custom CSS styling", value=True)
        
        if custom_styling:
            css_style = st.selectbox(
                "CSS style theme:",
                ["modern", "dark", "vintage", "minimal"],
                index=0,
                format_func=lambda x: x.capitalize()
            )
    
    # Generate map button
    st.markdown("<div style='text-align: center; margin: 20px 0;'>", unsafe_allow_html=True)
    generate_map = st.button("Generate Artistic Map", type="primary")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if generate_map:
        with st.spinner(f"Creating artistic {map_style} map for {location_method.lower()} {city if location_method == 'City Name' else f'({latitude:.4f}, {longitude:.4f})'}..."):
            # Create the artistic climate map
            m = simple_artistic_maps.create_artistic_climate_map(
                lat=latitude,
                lon=longitude,
                data_type=data_type,
                zoom=zoom_level,
                width=width,
                height=height,
                style=map_style
            )
            
            # Apply custom styling if requested
            if custom_styling:
                m = simple_artistic_maps.apply_style_to_map(m, style_name=css_style)
            
            # Add a watermark
            m.get_root().html.add_child(folium.Element(
                simple_artistic_maps.generate_map_watermark(text="Climate CoPilot")
            ))
            
            # Display the map
            folium_static(m, width=width, height=height)
            
            # Display color palette used
            style_mapping = {
                "ethereal": "climate_ethereal",
                "dramatic": "temperature_dramatic",
                "moody": "precipitation_moody",
                "surreal": "topography_surreal",
                "vibrant": "vegetation_vibrant",
                "neon": "urban_neon",
                "artistic": "artistic_terrain"
            }
            
            palette_name = style_mapping.get(map_style, "climate_ethereal")
            palette = simple_artistic_maps.ARTISTIC_PALETTES[palette_name]
            
            st.markdown(f"<h4 style='color: #1E90FF;'>Color Palette: {palette['name']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p>{palette['description']}</p>", unsafe_allow_html=True)
            
            # Display the color swatches as colored rectangles
            cols = st.columns(len(palette["colors"]))
            for i, color in enumerate(palette["colors"]):
                with cols[i]:
                    st.markdown(
                        f"""
                        <div style="background-color: {color}; height: 50px; width: 100%; 
                                  border-radius: 5px; margin: 5px 0;"></div>
                        """, 
                        unsafe_allow_html=True
                    )
    
    # Display information about the data sources
    st.markdown("<h3 style='color: #1E90FF;'>About the Maps</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: rgba(30, 30, 30, 0.6); padding: 15px; border-radius: 8px; margin-bottom: 10px;">
        <h4 style="color: #1E90FF; margin-top: 0;">Available Basemaps</h4>
        <ul style="color: white;">
            <li><strong>Dark Minimal:</strong> Clean, minimalist dark-themed basemap good for data visualization</li>
            <li><strong>Light Minimal:</strong> Bright, clean basemap with subtle features</li>
            <li><strong>Street Map:</strong> OpenStreetMap with detailed roads and infrastructure</li>
            <li><strong>Satellite:</strong> Esri World Imagery with high-resolution aerial photography</li>
            <li><strong>Topographic Map:</strong> OpenTopoMap with detailed terrain and elevation data</li>
            <li><strong>Terrain Relief:</strong> Stamen terrain map emphasizing natural features and landforms</li>
        </ul>
        
        <h4 style="color: #1E90FF; margin-top: 15px;">Toggleable Overlays</h4>
        <ul style="color: white;">
            <li><strong>Topography Lines:</strong> Contour lines that show elevation changes</li>
            <li><strong>Place Labels:</strong> City, town and street names that can be toggled on satellite view</li>
            <li><strong>Artistic Elements:</strong> Stylized overlay using the selected color palette</li>
        </ul>
        
        <h4 style="color: #1E90FF; margin-top: 15px;">Data Sources</h4>
        <ul style="color: white;">
            <li><strong>Topographic Data:</strong> OpenTopoMap provides topographic information based on OpenStreetMap and SRTM data</li>
            <li><strong>Satellite Imagery:</strong> Esri World Imagery provides satellite and aerial imagery</li>
            <li><strong>Base Maps:</strong> OpenStreetMap and CartoDB provide the underlying mapping infrastructure</li>
            <li><strong>Contour Lines:</strong> SRTM30 dataset provides global elevation contours</li>
        </ul>
        
        <h4 style="color: #1E90FF; margin-top: 15px;">Artistic Processing</h4>
        <p style="color: white;">
            The unique visual styles are created through a combination of:
        </p>
        <ul style="color: white;">
            <li>Custom-designed color palettes inspired by artistic movements and natural phenomena</li>
            <li>Interactive layers and stylized overlays that enhance geographic data</li>
            <li>Artistic gradients and custom CSS styling for a unique visual experience</li>
            <li>Cartographic styling techniques that balance visual appeal with scientific accuracy</li>
        </ul>
        
        <div style="margin-top: 15px; padding: 10px; border-radius: 5px; background-color: rgba(30, 144, 255, 0.2); color: white;">
            <p><strong>Tip:</strong> Use the layer control panel in the top-right corner of the map to toggle between different basemaps and overlays!</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    run_artistic_map_demo()