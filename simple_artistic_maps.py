"""
Simplified Artistic Map Module for Climate Copilot

This module provides unique, artistic map visualizations using Folium,
focusing on reliability over advanced image processing techniques.
"""

import folium
from folium.plugins import HeatMap, MiniMap, Fullscreen, MarkerCluster
import numpy as np
import random
import requests
import io
import os
import tempfile
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LightSource
import srtm_elevation
import nasa_ee_elevation

# Define custom color palettes for artistic rendering
ARTISTIC_PALETTES = {
    "climate_ethereal": {
        "description": "Dreamlike ethereal colors for climate visualization",
        "colors": ["#0D0887", "#41049D", "#6A00A8", "#8F0DA4", "#B12A90", "#D14B6F", "#ED7953", "#FDB32F", "#F0F921"],
        "name": "Ethereal"
    },
    "topography_surreal": {
        "description": "Surrealistic palette for topography",
        "colors": ["#00204D", "#143A6C", "#285C8C", "#3D7FAB", "#8BC2BD", "#B5DDCD", "#E3F7DE", "#FFFFFF"],
        "name": "Surreal Terrain"
    },
    "vegetation_vibrant": {
        "description": "Vibrant colors for vegetation visualization",
        "colors": ["#2D1160", "#39568C", "#477D85", "#5BA561", "#8FD744", "#C6E726", "#FEF720"],
        "name": "Vibrant Vegetation"
    },
    "temperature_dramatic": {
        "description": "Dramatic temperature gradient",
        "colors": ["#00007F", "#0000FF", "#00FFFF", "#FFFF00", "#FF7F00", "#7F0000"],
        "name": "Dramatic Temperature"
    },
    "precipitation_moody": {
        "description": "Moody blue-purple palette for precipitation",
        "colors": ["#F8F9FA", "#DCE3EF", "#BBC9E4", "#9AAFDA", "#7895CF", "#577BC4", "#3560B9", "#1346AE", "#002BA4"],
        "name": "Moody Rain"
    },
    "urban_neon": {
        "description": "Neon-inspired urban area visualization",
        "colors": ["#1A1A2E", "#16213E", "#0F3460", "#E94560", "#FF67E7", "#C400FF", "#52FFEE"],
        "name": "Neon Urban"
    },
    "artistic_terrain": {
        "description": "Artistic terrain style inspired by traditional cartography",
        "colors": ["#20283E", "#426A5A", "#63A375", "#A2D5AB", "#E5EEC1", "#FFFFFF"],
        "name": "Artistic Terrain"
    }
}

def create_artistic_topography_map(lat, lon, zoom=10, width=800, height=600, style="artistic_terrain", 
                              include_contours=True):
    """
    Create an artistic topographic map centered at the given coordinates
    
    Args:
        lat: Latitude
        lon: Longitude
        zoom: Zoom level (higher values zoom in more)
        width: Image width in pixels
        height: Image height in pixels
        style: Style name from ARTISTIC_PALETTES
        include_contours: Whether to include elevation contour lines
    
    Returns:
        Folium map with artistic styling
    """
    # Create the base map with no tiles initially
    m = folium.Map(
        location=[lat, lon],
        zoom_start=zoom,
        tiles=None,
        width=width,
        height=height
    )
    
    # Use Google's terrain view (p = terrain with labels)
    folium.TileLayer(
        name='Terrain with Labels',
        tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
        attr='Google Maps',
    ).add_to(m)
    
    # Use Google's satellite imagery with labels (y = hybrid with labels)
    folium.TileLayer(
        name='Satellite with Labels',
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google Maps',
    ).add_to(m)
    
    # Use Google's satellite imagery without labels (s = satellite only)
    folium.TileLayer(
        name='Satellite',
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Maps',
    ).add_to(m)
    
    # Standard OpenStreetMap
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="Street Map",
        control=True,
    ).add_to(m)
    
    # Dark minimal basemap
    folium.TileLayer(
        tiles="cartodbdark_matter",
        name="Dark Mode",
        control=True,
    ).add_to(m)
    
    # Light minimal basemap
    folium.TileLayer(
        tiles="cartodbpositron",
        name="Light Mode",
        control=True,
    ).add_to(m)
    
    # Add elevation contour lines as a toggleable overlay
    if include_contours:
        # If we're at a higher zoom level (zoomed in more), we need more detailed contours
        contour_width = 100 if zoom > 12 else 80
        contour_height = 100 if zoom > 12 else 80
        num_contours = 20 if zoom > 12 else 15
        
        # Choose contour color based on style or use a default purple
        contour_color = '#6644aa'  # Default purple that works on most backgrounds
        if style in ARTISTIC_PALETTES and len(ARTISTIC_PALETTES[style]["colors"]) > 0:
            contour_color = ARTISTIC_PALETTES[style]["colors"][0]
            
        # Add the contour lines with elevation data in meters
        try:
            m = add_contour_lines_to_map(
                m, lat, lon, zoom=zoom, 
                contour_width=2,
                contour_color=contour_color,
                num_contours=num_contours,
                width=contour_width, 
                height=contour_height,
                use_feet=False
            )
        except Exception as e:
            print(f"Failed to add contour lines (meters): {e}")
        
        # Add the contour lines with elevation data in feet
        try:
            m = add_contour_lines_to_map(
                m, lat, lon, zoom=zoom, 
                contour_width=2,
                contour_color='#44aaaa',  # Different color for feet contours
                num_contours=num_contours,
                width=contour_width, 
                height=contour_height,
                use_feet=True
            )
        except Exception as e:
            print(f"Failed to add contour lines (feet): {e}")
    
    # Store the palette information for reference, but don't add artistic elements
    if style in ARTISTIC_PALETTES:
        palette = ARTISTIC_PALETTES[style]
        # We'll just use this for attribution/display purposes but not add decorative elements
    
    # Add a minimap for context
    minimap = MiniMap(toggle_display=True, position='bottomright')
    m.add_child(minimap)
    
    # Add fullscreen control
    Fullscreen(position='topleft').add_to(m)
    
    # Add layer control - positioned top right for easy access
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    # Add custom attribution
    attribution = f'Climate Copilot Artistic Topography | Style: {ARTISTIC_PALETTES[style]["name"] if style in ARTISTIC_PALETTES else "Custom"}'
    m.get_root().html.add_child(folium.Element(f'''
        <div style="position: fixed; bottom: 10px; left: 10px; z-index: 1000; 
                  background-color: rgba(0, 0, 0, 0.7); padding: 5px; border-radius: 5px;
                  font-size: 11px; font-family: Arial; color: white;">
            {attribution}
        </div>
    '''))
    
    return m

def create_artistic_satellite_map(lat, lon, zoom=10, width=800, height=600, style="climate_ethereal", 
                            data_type="satellite", include_contours=True):
    """
    Create an artistic map based on satellite imagery
    
    Args:
        lat: Latitude
        lon: Longitude
        zoom: Zoom level
        width: Image width in pixels
        height: Image height in pixels
        style: Style name from ARTISTIC_PALETTES
        data_type: Type of map (used to determine if this is a satellite view)
        include_contours: Whether to include elevation contour lines
    
    Returns:
        Folium map with artistic satellite imagery
    """
    # Create the base map with no tiles initially
    m = folium.Map(
        location=[lat, lon],
        zoom_start=zoom,
        tiles=None,
        width=width,
        height=height
    )
    
    # Use Google's satellite imagery with labels directly (y = hybrid with labels)
    folium.TileLayer(
        name='Satellite with Labels',
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google Maps',
    ).add_to(m)
    
    # Use Google's satellite imagery without labels (s = satellite only)
    folium.TileLayer(
        name='Satellite',
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google Maps',
    ).add_to(m)
    
    # Dark minimal basemap
    folium.TileLayer(
        tiles="cartodbdark_matter",
        name="Dark Mode",
        control=True,
    ).add_to(m)
    
    # Light minimal basemap
    folium.TileLayer(
        tiles="cartodbpositron",
        name="Light Mode",
        control=True,
    ).add_to(m)
    
    # Standard OpenStreetMap
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="Street Map",
        control=True,
    ).add_to(m)
    
    # Add elevation contour lines as a toggleable overlay
    if include_contours:
        # If we're at a higher zoom level (zoomed in more), we need more detailed contours
        contour_width = 100 if zoom > 12 else 80
        contour_height = 100 if zoom > 12 else 80
        num_contours = 20 if zoom > 12 else 15
        
        # For satellite view, use white contours with black outline that will be visible
        contour_color = '#ffffff'
            
        # Add the contour lines with elevation data in meters
        try:
            m = add_contour_lines_to_map(
                m, lat, lon, zoom=zoom, 
                contour_width=2,
                contour_color=contour_color,
                num_contours=num_contours,
                width=contour_width, 
                height=contour_height,
                use_feet=False
            )
        except Exception as e:
            print(f"Failed to add contour lines (meters): {e}")
        
        # Add the contour lines with elevation data in feet
        try:
            m = add_contour_lines_to_map(
                m, lat, lon, zoom=zoom, 
                contour_width=2,
                contour_color='#ffce00',  # Yellow for feet contours on satellite
                num_contours=num_contours,
                width=contour_width, 
                height=contour_height,
                use_feet=True
            )
        except Exception as e:
            print(f"Failed to add contour lines (feet): {e}")
    
    # Store the palette information for reference, but don't add artistic elements
    if style in ARTISTIC_PALETTES:
        palette = ARTISTIC_PALETTES[style]
        # Just use for attribution/display
    
    # Add a minimap for context
    minimap = MiniMap(toggle_display=True, position='bottomright')
    m.add_child(minimap)
    
    # Add fullscreen control
    Fullscreen(position='topleft').add_to(m)
    
    # Add layer control - positioned top right for easy access
    folium.LayerControl(position='topright', collapsed=False).add_to(m)
    
    # Add custom attribution
    attribution = f'Climate Copilot Artistic Satellite View | Style: {ARTISTIC_PALETTES[style]["name"] if style in ARTISTIC_PALETTES else "Custom"}'
    m.get_root().html.add_child(folium.Element(f'''
        <div style="position: fixed; bottom: 10px; left: 10px; z-index: 1000; 
                  background-color: rgba(0, 0, 0, 0.7); padding: 5px; border-radius: 5px;
                  font-size: 11px; font-family: Arial; color: white;">
            {attribution}
        </div>
    '''))
    
    return m

def create_artistic_climate_map(lat, lon, data_type="topography", 
                               zoom=10, width=800, height=600, style="ethereal", include_contours=True):
    """
    Create an artistic climate map with the specified data overlay
    
    Args:
        lat: Latitude
        lon: Longitude
        data_type: Type of map ("topography", "satellite")
        zoom: Zoom level
        width: Map width in pixels
        height: Map height in pixels
        style: Artistic style
        include_contours: Whether to include elevation contour lines
    
    Returns:
        Folium map
    """
    # Map styles to palettes
    style_mapping = {
        "ethereal": "climate_ethereal",
        "dramatic": "temperature_dramatic",
        "moody": "precipitation_moody",
        "surreal": "topography_surreal",
        "vibrant": "vegetation_vibrant",
        "neon": "urban_neon",
        "artistic": "artistic_terrain"
    }
    
    palette = style_mapping.get(style, "climate_ethereal")
    
    # Create appropriate map based on data type
    if data_type == "topography":
        return create_artistic_topography_map(
            lat, lon, zoom=zoom, width=width, height=height, style=palette,
            include_contours=include_contours
        )
    elif data_type == "satellite":
        return create_artistic_satellite_map(
            lat, lon, zoom=zoom, width=width, height=height, style=palette, 
            data_type=data_type, include_contours=include_contours
        )
    else:
        # Default to topography
        return create_artistic_topography_map(
            lat, lon, zoom=zoom, width=width, height=height, style=palette,
            include_contours=include_contours
        )

def apply_style_to_map(m, style_name="modern"):
    """
    Apply custom CSS styling to a folium map
    
    Args:
        m: Folium map
        style_name: Style to apply ("modern", "dark", "vintage", "minimal")
    
    Returns:
        Folium map with custom styling
    """
    styles = {
        "modern": """
            .leaflet-container { background: #1a1a2e; }
            .leaflet-control-zoom { border-radius: 15px; overflow: hidden; }
            .leaflet-control-zoom a { background: #0f3460 !important; color: white !important; border: none !important; }
            .leaflet-control-zoom a:hover { background: #e94560 !important; }
            .leaflet-control-attribution { background: rgba(0,0,0,0.7) !important; color: #aaa !important; }
        """,
        "dark": """
            .leaflet-container { background: #121212; }
            .leaflet-control-zoom { border-radius: 0; overflow: hidden; }
            .leaflet-control-zoom a { background: #333 !important; color: #ddd !important; border: none !important; }
            .leaflet-control-zoom a:hover { background: #555 !important; }
            .leaflet-control-attribution { background: rgba(0,0,0,0.8) !important; color: #888 !important; }
        """,
        "vintage": """
            .leaflet-container { background: #f0e7d8; }
            .leaflet-control-zoom { border-radius: 0; border: 1px solid #8b7765; overflow: hidden; }
            .leaflet-control-zoom a { background: #d5c7b5 !important; color: #6d5c4e !important; border: none !important; }
            .leaflet-control-zoom a:hover { background: #8b7765 !important; color: #f0e7d8 !important; }
            .leaflet-control-attribution { background: rgba(213,199,181,0.7) !important; color: #6d5c4e !important; }
        """,
        "minimal": """
            .leaflet-container { background: #f9f9f9; }
            .leaflet-control-zoom { border-radius: 5px; overflow: hidden; box-shadow: none; }
            .leaflet-control-zoom a { background: white !important; color: #333 !important; border: 1px solid #eee !important; }
            .leaflet-control-zoom a:hover { background: #eee !important; }
            .leaflet-control-attribution { background: rgba(255,255,255,0.7) !important; color: #999 !important; }
        """
    }
    
    # Add the custom CSS style
    style = styles.get(style_name, styles["modern"])
    m.get_root().html.add_child(folium.Element(f'<style>{style}</style>'))
    
    return m

def generate_map_watermark(text="Climate CoPilot"):
    """
    Generate an artistic watermark for the map
    
    Args:
        text: Watermark text
    
    Returns:
        HTML string for the watermark
    """
    return f'''
    <div style="position: fixed; bottom: 20px; right: 20px; z-index: 1000; 
              background-color: rgba(0, 0, 0, 0.5); padding: 8px 15px; border-radius: 20px;
              font-size: 14px; font-family: 'Helvetica Neue', Arial; color: white;
              letter-spacing: 1px; font-weight: 300; pointer-events: none;">
        {text}
    </div>
    '''

def fetch_elevation_data(lat, lon, width=100, height=100, zoom=10):
    """
    Fetch elevation data from NASA Earth Explorer or SRTM dataset for the given coordinates
    
    Args:
        lat: Center latitude
        lon: Center longitude
        width: Number of points in x direction
        height: Number of points in y direction
        zoom: Zoom level (controls the area size)
    
    Returns:
        Numpy array of elevation data, bounds tuple (min_lon, min_lat, max_lon, max_lat)
    """
    try:
        # Calculate bounding box radius based on zoom level
        # Higher zoom = smaller area
        # This formula gives reasonable areas at different zoom levels
        scale_factor = 10.0 / (2**zoom)
        radius = scale_factor / 2
        
        # First try NASA Earth Explorer with authenticated access - highest quality
        print(f"Fetching NASA Earth Explorer elevation data for {lat}, {lon} with radius {radius} degrees")
        elevation_data, bounds = nasa_ee_elevation.fetch_elevation_data(
            lat=lat, 
            lon=lon, 
            width=width, 
            height=height,
            radius=radius
        )
        
        # If Earth Explorer data is available, use it
        if elevation_data is not None:
            print(f"Successfully fetched NASA Earth Explorer elevation data with shape {elevation_data.shape}")
            # Replace NaN values with median to avoid contour problems
            if np.isnan(elevation_data).any():
                median = np.nanmedian(elevation_data)
                elevation_data = np.nan_to_num(elevation_data, nan=median)
            return elevation_data, bounds
        
        # If Earth Explorer fails, try our direct SRTM module (backup method)
        print(f"Earth Explorer failed, falling back to SRTM. Fetching data for {lat}, {lon}")
        elevation_data, bounds = srtm_elevation.fetch_elevation_array(
            lat=lat, 
            lon=lon, 
            width=width, 
            height=height,
            radius=radius
        )
        
        # If SRTM data is available, use it
        if elevation_data is not None:
            print(f"Successfully fetched SRTM elevation data with shape {elevation_data.shape}")
            # Replace NaN values with median to avoid contour problems
            if np.isnan(elevation_data).any():
                median = np.nanmedian(elevation_data)
                elevation_data = np.nan_to_num(elevation_data, nan=median)
            return elevation_data, bounds
        
        # If both methods failed, we have to use synthetic data
        raise Exception("Both NASA Earth Explorer and SRTM data sources failed")
        
    except Exception as e:
        # Calculate bounds for the synthetic data
        scale_factor = 10.0 / (2**zoom)
        
        # Calculate the bounds
        lon_range = scale_factor
        lat_range = scale_factor
        
        min_lon = lon - lon_range/2
        max_lon = lon + lon_range/2
        min_lat = lat - lat_range/2
        max_lat = lat + lat_range/2
        
        bounds = (min_lon, min_lat, max_lon, max_lat)
        
        print(f"Failed to fetch elevation data: {e}")
        print("Falling back to synthetic elevation data")
        
        # If both data sources fail, fall back to synthetic data with bounds
        return srtm_elevation.generate_synthetic_elevation(width, height, bounds), bounds



def add_contour_lines_to_map(m, lat, lon, zoom=10, contour_width=2, contour_color='#6644aa', 
                           num_contours=15, width=100, height=100, use_feet=False):
    """
    Add elevation contour lines directly to Folium map
    
    Args:
        m: Folium map object
        lat: Center latitude
        lon: Center longitude
        zoom: Zoom level
        contour_width: Line width for contours
        contour_color: Color of contour lines
        num_contours: Number of contour lines to draw
        width: Grid width for elevation data
        height: Grid height for elevation data
        use_feet: Whether to display elevations in feet instead of meters
    
    Returns:
        Updated Folium map with contour overlay
    """
    try:
        # Fetch elevation data
        elevation_data, bounds = fetch_elevation_data(lat, lon, width, height, zoom)
        
        # Generate contour lines
        min_elevation = np.min(elevation_data)
        max_elevation = np.max(elevation_data)
        
        # Convert to feet if requested
        if use_feet:
            # 1 meter = 3.28084 feet
            elevation_data = elevation_data * 3.28084
            min_elevation = min_elevation * 3.28084
            max_elevation = max_elevation * 3.28084
            unit = "ft"
        else:
            unit = "m"
        
        # Create levels for contour lines
        levels = np.linspace(min_elevation, max_elevation, num_contours)
        
        # Create a meshgrid for plotting
        x = np.linspace(bounds[0], bounds[2], width)
        y = np.linspace(bounds[1], bounds[3], height)
        X, Y = np.meshgrid(x, y)
        
        # We'll use folium's features to add contour lines directly
        # Create a feature group for the contours
        contour_group = folium.FeatureGroup(name=f"Elevation Contours ({unit})", overlay=True, control=True)
        
        # Generate contours
        for level in levels:
            # Add elevation contour lines directly using GeoJson
            # For each level, create a simplified contour polygon
            # This is a simple algorithm to create linear contour lines
            contour_points = []
            for i in range(width-1):
                for j in range(height-1):
                    # Check if contour passes through this cell (simplified approach)
                    if ((elevation_data[j, i] <= level and elevation_data[j+1, i] >= level) or
                        (elevation_data[j, i] >= level and elevation_data[j+1, i] <= level) or
                        (elevation_data[j, i] <= level and elevation_data[j, i+1] >= level) or
                        (elevation_data[j, i] >= level and elevation_data[j, i+1] <= level)):
                        
                        contour_points.append([Y[j, i], X[j, i]])
            
            # If we have points for this contour, add it to the map
            if contour_points:
                # Create a line string for the contour
                folium.PolyLine(
                    locations=contour_points,
                    color=contour_color,
                    weight=contour_width,
                    opacity=0.7,
                    tooltip=f"Elevation: {int(level)} {unit}",
                ).add_to(contour_group)
        
        # Add the contour group to the map
        contour_group.add_to(m)
        
        return m
    except Exception as e:
        unit_label = "ft" if use_feet else "m"
        print(f"Failed to add contour lines ({unit_label}): {e}")
        # Continue without contours if there's an error
        return m