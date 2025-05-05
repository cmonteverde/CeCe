"""
Interactive Globe Map Module for Climate Copilot

This module provides an interactive 3D globe visualization using Plotly
that can be embedded within the main application. The globe features:
- Dark/light mode toggle
- Color scheme matching the CeCe brand colors
- Full globe view at startup
- Interactive zoom and rotation
- Optional data layers for climate visualization
- High-resolution topography and terrain data when zoomed in
"""

import plotly.graph_objects as go
import numpy as np
import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static

# CeCe brand colors (blue to purple gradient)
CECE_BLUE = "#1E90FF"
CECE_PURPLE = "#9370DB"
CECE_GRADIENT = [CECE_BLUE, "#5F7FEA", "#8A6CD7", CECE_PURPLE]

# High-resolution map tile sources
TERRAIN_TILES = {
    "dark": {
        "base": "CartoDB dark_matter",
        "topo": "https://tile.opentopomap.org/{z}/{x}/{y}.png",
        "roads": "https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
        "satellite": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "relief": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}",
        "terrain": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}"
    },
    "light": {
        "base": "CartoDB positron",
        "topo": "https://tile.opentopomap.org/{z}/{x}/{y}.png",
        "roads": "https://a.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
        "satellite": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "relief": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Shaded_Relief/MapServer/tile/{z}/{y}/{x}",
        "terrain": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Terrain_Base/MapServer/tile/{z}/{y}/{x}"
    }
}

def create_globe_map(dark_mode=True, width=800, height=600):
    """
    Create an interactive 3D globe visualization
    
    Args:
        dark_mode: Whether to use dark mode (True) or light mode (False)
        width: Width of the map in pixels (default: 800)
        height: Height of the map in pixels
        
    Returns:
        Plotly figure object
    """
    # Base colors for dark and light modes
    if dark_mode:
        land_color = "#2D2D2D"
        ocean_color = "#0D1117"
        bg_color = "rgba(0,0,0,0)"
        text_color = "white"
        grid_color = "#444"
        coast_color = CECE_BLUE  # Use CeCe blue for coastlines in dark mode
        country_color = "#555"
    else:
        land_color = "#E5E5E5" 
        ocean_color = "#EAEAEF"
        bg_color = "rgba(255,255,255,0)"
        text_color = "#333"
        grid_color = "#ddd"
        coast_color = CECE_PURPLE  # Use CeCe purple for coastlines in light mode
        country_color = "#777"
    
    # Create the base figure with a globe projection
    fig = go.Figure()
    
    # Add the base globe with land and ocean
    fig.add_trace(go.Choropleth(
        locationmode="country names",
        z=[1] * 250,  # Dummy data for coloring
        colorscale=[[0, land_color], [1, land_color]],
        marker_line_color=country_color,
        marker_line_width=0.5,  # Always show country lines
        showscale=False,
        hoverinfo="skip"
    ))
    
    # Create gradient-colored markers for key latitudes with CeCe colors
    latitudes = np.linspace(-60, 60, len(CECE_GRADIENT))
    for i, lat in enumerate(latitudes):
        color = CECE_GRADIENT[i]
        # Add subtle latitude markers with CeCe brand colors
        lons = np.linspace(-180, 180, 100)
        lats = np.full_like(lons, lat)
        
        fig.add_trace(go.Scattergeo(
            lon=lons,
            lat=lats,
            mode="lines",
            line=dict(width=1.5, color=color, dash="dot"),
            opacity=0.4,
            hoverinfo="skip",
            showlegend=False
        ))
    
    # Configure the 3D projection and interactivity
    fig.update_geos(
        projection_type="orthographic",
        showcoastlines=True, coastlinecolor=coast_color,
        showland=True, landcolor=land_color,
        showocean=True, oceancolor=ocean_color,
        showlakes=True, lakecolor=ocean_color,
        showcountries=True,  # Always show country lines
        countrycolor=country_color,
        showframe=False,
        framecolor=grid_color,
        showsubunits=False,
        showrivers=False,
        lataxis=dict(gridcolor=grid_color, showgrid=True, gridwidth=0.5),
        lonaxis=dict(gridcolor=grid_color, showgrid=True, gridwidth=0.5),
        resolution=50,
        bgcolor=bg_color,
        # Maximize the globe's display within its container
        fitbounds="locations",
        visible=True
    )
    
    # Update the layout to make it more expansive and improve zoom
    fig.update_layout(
        title=None,
        width=width,  # None for full container width
        height=height,
        autosize=True,  # Enable autosize for responsive behavior
        margin=dict(l=0, r=0, t=0, b=0, pad=0),  # Remove all margins
        paper_bgcolor=bg_color,
        plot_bgcolor=bg_color,
        geo=dict(
            projection_rotation=dict(lon=0, lat=0, roll=0),
            # Start with a view of the full globe
            center=dict(lon=0, lat=0),
            # Maximize the globe size within the container
            projection_scale=1.0,  # Full size projection
            # Allow for more interactive zoom range
            scope="world"
        ),
        font=dict(color=text_color),
        # Enhanced display settings for better appearance
        dragmode="pan",  # Change to "pan" for better touch interaction
        # Enable direct zoom control
        modebar=dict(
            orientation="v",
            bgcolor="rgba(0,0,0,0)",
            color=text_color,
            activecolor=coast_color
        )
    )
    
    return fig

def add_climate_layer(fig, layer_type="temperature", data=None):
    """
    Add a climate data visualization layer to the globe
    
    Args:
        fig: Plotly figure object (globe)
        layer_type: Type of climate layer ("temperature", "precipitation", etc.)
        data: Climate data to visualize
        
    Returns:
        Updated Plotly figure
    """
    # If no data is provided, create sample data for demonstration
    if data is None:
        if layer_type == "temperature":
            # Generate sample temperature data
            lats = np.linspace(-90, 90, 37)
            lons = np.linspace(-180, 180, 73)
            lon_grid, lat_grid = np.meshgrid(lons, lats)
            
            # Create a sample temperature pattern (warmer at equator, cooler at poles)
            temp_data = 20 * np.cos(np.radians(lat_grid)) - 5 * np.random.rand(*lat_grid.shape)
            
            # Convert to flat arrays for Plotly
            lats_flat = lat_grid.flatten()
            lons_flat = lon_grid.flatten()
            temp_flat = temp_data.flatten()
            
            # Add temperature heatmap
            fig.add_trace(go.Densitymapbox(
                lat=lats_flat,
                lon=lons_flat,
                z=temp_flat,
                radius=15,
                colorscale=[
                    [0, "#0d47a1"],  # Cold (deep blue)
                    [0.5, CECE_BLUE],  # Medium (CeCe blue)
                    [0.75, "#9370DB"],  # Warm (CeCe purple)
                    [1, "#b71c1c"]  # Hot (red)
                ],
                opacity=0.6,
                showscale=True,
                colorbar=dict(
                    title="Temp (°C)",
                    titleside="top",
                    outlinewidth=0,
                    borderwidth=0,
                    thickness=15
                ),
                hovertemplate="Lat: %{lat:.2f}<br>Lon: %{lon:.2f}<br>Temp: %{z:.1f}°C<extra></extra>"
            ))
    
    return fig

def create_detailed_terrain_map(lat=0, lon=0, zoom=3, dark_mode=True):
    """
    Create a detailed terrain map with high-resolution topography and features
    
    Args:
        lat: Latitude center point
        lon: Longitude center point
        zoom: Initial zoom level (higher values show more detail)
        dark_mode: Whether to use dark mode
        
    Returns:
        Folium map object with high-resolution terrain
    """
    # Select appropriate tile style based on dark/light mode
    mode = "dark" if dark_mode else "light"
    base_tiles = TERRAIN_TILES[mode]
    
    # Create base map with the appropriate base tile
    m = folium.Map(
        location=[lat, lon],
        zoom_start=zoom,
        tiles=base_tiles["base"],
        control_scale=True,
        width="100%"
    )
    
    # Add all available terrain and feature layers
    
    # Topography layer (shows elevation contours)
    topo_layer = folium.TileLayer(
        tiles=base_tiles["topo"],
        name="Topography",
        overlay=True,
        opacity=0.7,
        attr="OpenTopoMap"
    )
    topo_layer.add_to(m)
    
    # Roads and streets layer (shows streets, highways, etc.)
    roads_layer = folium.TileLayer(
        tiles=base_tiles["roads"],
        name="Roads",
        overlay=True,
        opacity=0.8,
        attr="OSM Humanitarian"
    )
    roads_layer.add_to(m)
    
    # Satellite imagery layer
    satellite_layer = folium.TileLayer(
        tiles=base_tiles["satellite"],
        name="Satellite",
        overlay=True,
        opacity=0.9,
        attr="ESRI World Imagery"
    )
    satellite_layer.add_to(m)
    
    # Terrain relief layer (shows shaded terrain)
    relief_layer = folium.TileLayer(
        tiles=base_tiles["relief"],
        name="Relief",
        overlay=True,
        opacity=0.6,
        attr="ESRI Shaded Relief"
    )
    relief_layer.add_to(m)
    
    # Enhanced terrain base layer
    terrain_layer = folium.TileLayer(
        tiles=base_tiles["terrain"],
        name="Terrain Base",
        overlay=True,
        opacity=0.7,
        attr="ESRI Terrain Base"
    )
    terrain_layer.add_to(m)
    
    # Add a fullscreen control
    folium.plugins.Fullscreen(
        position="topleft",
        title="Expand map",
        title_cancel="Exit fullscreen",
        force_separate_button=True,
    ).add_to(m)
    
    # Add a scale bar and measurement tools
    folium.plugins.MeasureControl(
        position="bottomleft",
        primary_length_unit="kilometers",
        secondary_length_unit="miles",
        primary_area_unit="sqmeters",
        secondary_area_unit="acres"
    ).add_to(m)
    
    # Add a mini map for context and orientation
    minimap = folium.plugins.MiniMap(
        toggle_display=True,
        position="bottomright",
        tile_layer=base_tiles["base"],
        zoom_level_offset=-5,
        width=150,
        height=150
    )
    m.add_child(minimap)
    
    # Add layer control to toggle between different map views
    folium.LayerControl(position="topright", collapsed=False).add_to(m)
    
    # Add CeCe branding watermark
    brand_html = f"""
    <div style="
        position: absolute; 
        bottom: 10px; 
        left: 10px; 
        z-index: 1000;
        background-color: {'rgba(0,0,0,0.6)' if dark_mode else 'rgba(255,255,255,0.6)'};
        color: {'white' if dark_mode else 'black'};
        padding: 5px 10px;
        border-radius: 5px;
        font-weight: bold;
        font-size: 12px;
    ">
        <span style="background: linear-gradient(90deg, #1E90FF, #9370DB); 
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;">
            CeCe Detailed Terrain Map
        </span>
    </div>
    """
    m.get_root().html.add_child(folium.Element(brand_html))
    
    # When clicking on the map, show coordinates and elevation data
    m.add_child(folium.LatLngPopup())
    
    return m

def display_globe_map(dark_mode=True):
    """Display the interactive globe map in Streamlit
    
    Args:
        dark_mode: Whether to use dark mode (True) or light mode (False)
    """
    # Create container for the map with styling
    st.markdown("""
    <div style="margin-top: 30px; margin-bottom: 30px; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3); width: 100%;">
        <div style="background: linear-gradient(90deg, #1E90FF, #9370DB); height: 4px;"></div>
        <div id="globe-container" style="width: 100%;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Create columns for controls - removed Show Countries checkbox as it's always on
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        st.markdown("""
        <div style="background: linear-gradient(90deg, #1E90FF, #9370DB); 
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-weight: bold;
                    font-size: 18px;
                    margin-top: 5px;">
            CeCe Global Climate Explorer
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        dark_mode = st.checkbox("Dark Mode", value=dark_mode)
    
    with col3:
        layer_type = st.selectbox("Data Layer", ["None", "Temperature", "Precipitation"], index=0)
    
    with col4:
        map_type = st.selectbox("Map Type", ["Globe", "Terrain"], index=0)
    
    # Store the map type preference
    if 'map_type' not in st.session_state:
        st.session_state.map_type = map_type
    else:
        st.session_state.map_type = map_type
        
    # Determine the ideal dimensions based on the viewport
    height = 600  # Taller map for better visibility
    
    # Display different map types based on selection
    if st.session_state.map_type == "Globe":
        # Create the globe map (lower resolution but 3D)
        fig = create_globe_map(dark_mode=dark_mode, width=800, height=height)
        
        # Add climate layer if selected
        if layer_type.lower() != "none":
            fig = add_climate_layer(fig, layer_type=layer_type.lower())
        
        # Make the chart responsive and fill the container
        st.plotly_chart(fig, use_container_width=True, config={
            'displayModeBar': True,
            'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
            'displaylogo': False,
            'responsive': True,
            'scrollZoom': True,
            'doubleClick': 'reset+autosize',  # Reset view on double click
            'toImageButtonOptions': {
                'format': 'png',
                'filename': 'climate_globe',
                'height': 800,
                'width': 1200
            }
        })
    else:
        # Create high-resolution terrain map (flat but detailed)
        detailed_map = create_detailed_terrain_map(
            lat=0, 
            lon=0, 
            zoom=3, 
            dark_mode=dark_mode
        )
        
        # Add a note about the map's capabilities
        st.markdown("""
        <div style="font-size: 14px; color: #888; text-align: center; margin-bottom: 10px;">
            Zoom in to see detailed topography, roads, cities and terrain features.
            Toggle layers using the control panel in the top right.
        </div>
        """, unsafe_allow_html=True)
        
        # Display the interactive folium map
        folium_static(detailed_map, width=None, height=height-50)