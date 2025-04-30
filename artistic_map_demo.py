"""
Artistic Map Demo for Climate Copilot

This module demonstrates the artistic map capabilities
of the Climate Copilot application, showcasing high-resolution
topography, land use data, and stylized satellite imagery.
"""

import streamlit as st
import folium
from folium.plugins import HeatMap, MarkerCluster
try:
    from streamlit_folium import folium_static
except ImportError:
    # Fallback for streamlit_folium import error
    st.error("streamlit_folium package is not available. Please install it using: pip install streamlit-folium")
    
    # Define a simple function to handle the fallback case
    def folium_static(folium_map, width=None, height=None):
        """Fallback function if streamlit_folium is not available"""
        html = folium_map._repr_html_()
        st.components.v1.html(html, width=width, height=height)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import io
import base64
from PIL import Image

# Import our artistic map module
import artistic_maps

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
        city = st.text_input("Enter city name:", "Paris")
        try:
            # Use the existing function from the main app to get coordinates
            from app import get_city_coordinates
            latitude, longitude = get_city_coordinates(city)
            st.success(f"Coordinates: {latitude:.4f}, {longitude:.4f}")
        except Exception as e:
            st.error(f"Could not find coordinates for '{city}'. Please try another city name.")
            st.stop()
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
            
        artistic_effects = st.checkbox("Apply artistic effects", value=True)
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
            m = artistic_maps.create_artistic_climate_map(
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
                m = artistic_maps.apply_style_to_map(m, style_name=css_style)
            
            # Add a watermark
            if artistic_effects:
                m.get_root().html.add_child(folium.Element(
                    artistic_maps.generate_map_watermark(text="Climate CoPilot")
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
            palette = artistic_maps.ARTISTIC_PALETTES[palette_name]
            
            st.markdown(f"<h4 style='color: #1E90FF;'>Color Palette: {palette['name']}</h4>", unsafe_allow_html=True)
            st.markdown(f"<p>{palette['description']}</p>", unsafe_allow_html=True)
            
            # Display the color swatches
            colors = palette["colors"]
            fig, ax = plt.subplots(figsize=(10, 1))
            ax.imshow([np.arange(len(colors))], cmap=artistic_maps.create_custom_colormap(palette_name))
            ax.set_xticks(np.arange(len(colors)))
            ax.set_xticklabels([])
            ax.set_yticks([])
            st.pyplot(fig)
    
    # Display information about the data sources
    st.markdown("<h3 style='color: #1E90FF;'>About the Maps</h3>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: rgba(30, 30, 30, 0.6); padding: 15px; border-radius: 8px; margin-bottom: 10px;">
        <h4 style="color: #1E90FF; margin-top: 0;">Data Sources</h4>
        <ul style="color: white;">
            <li><strong>Topographic Data:</strong> SRTM (Shuttle Radar Topography Mission) elevation data provides high-resolution terrain information, with global coverage at approximately 30m resolution.</li>
            <li><strong>Satellite Imagery:</strong> High-resolution satellite imagery from various sources including Sentinel-2 (10m resolution) and Landsat-8 (30m resolution).</li>
            <li><strong>Land Use Data:</strong> Land cover and land use information from global land cover databases and regional classifications.</li>
            <li><strong>Base Maps:</strong> OpenStreetMap and CartoDB provide the underlying mapping infrastructure.</li>
        </ul>
        
        <h4 style="color: #1E90FF;">Artistic Processing</h4>
        <p style="color: white;">
            The unique visual styles are created through a combination of:
        </p>
        <ul style="color: white;">
            <li>Custom-designed color palettes inspired by artistic movements and natural phenomena</li>
            <li>Advanced image processing techniques including contrast enhancement, color manipulation, and artistic filters</li>
            <li>Multi-layer compositing that blends different data sources to create rich, informative visualizations</li>
            <li>Cartographic styling techniques that balance visual appeal with scientific accuracy</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    run_artistic_map_demo()