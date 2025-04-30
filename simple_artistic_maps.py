"""
Simplified Artistic Map Module for Climate Copilot

This module provides unique, artistic map visualizations using Folium,
focusing on reliability over advanced image processing techniques.
"""

import folium
from folium.plugins import HeatMap, MiniMap, Fullscreen, MarkerCluster
import numpy as np
import random

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

def create_artistic_topography_map(lat, lon, zoom=10, width=800, height=600, style="artistic_terrain"):
    """
    Create an artistic topographic map centered at the given coordinates
    
    Args:
        lat: Latitude
        lon: Longitude
        zoom: Zoom level (higher values zoom in more)
        width: Image width in pixels
        height: Image height in pixels
        style: Style name from ARTISTIC_PALETTES
    
    Returns:
        Folium map with artistic styling
    """
    # Create base map with a dark theme as default
    m = folium.Map(
        location=[lat, lon],
        zoom_start=zoom,
        tiles=None,  # Start with no base tiles to allow selection
        width=width,
        height=height
    )
    
    # Add multiple basemap options that users can toggle between
    # 1. Dark minimal basemap (default)
    folium.TileLayer(
        tiles="cartodbdark_matter",
        name="Dark Minimal",
        control=True,
    ).add_to(m)
    
    # 2. Light minimal basemap
    folium.TileLayer(
        tiles="cartodbpositron",
        name="Light Minimal",
        control=True,
    ).add_to(m)
    
    # 3. Standard OpenStreetMap
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="Street Map",
        control=True,
    ).add_to(m)
    
    # 4. Satellite imagery
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite',
        control=True,
    ).add_to(m)
    
    # 5. Topographic full map
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a>',
        name='Topographic Map',
        control=True,
    ).add_to(m)
    
    # 6. Relief map from Stamen
    try:
        folium.TileLayer(
            tiles='https://stamen-tiles-{s}.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png',
            attr='Map tiles by <a href="http://stamen.com">Stamen Design</a>, under <a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a>',
            name='Terrain Relief',
            control=True,
        ).add_to(m)
    except:
        # If Stamen tiles fail, use another tile source
        pass

    # Add Topography Lines overlay (can be toggled on/off)
    # Using OpenTopoMap contour lines which are more reliable
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='Map data: &copy; OpenStreetMap contributors, SRTM | Style: &copy; OpenTopoMap',
        name='Topography Lines',
        overlay=True,  # Important: make it an overlay, not a base layer
        opacity=0.6,
        control=True,
    ).add_to(m)
    
    # Add a labels overlay for satellite view
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png',
        attr='&copy; CartoDB',
        name='Place Labels',
        overlay=True,  # This makes it an overlay that can be toggled
        opacity=0.9,
        control=True,
    ).add_to(m)
    
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

def create_artistic_satellite_map(lat, lon, zoom=10, width=800, height=600, style="climate_ethereal", data_type="satellite"):
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
    
    Returns:
        Folium map with artistic satellite imagery
    """
    # Create base map with satellite imagery as default
    m = folium.Map(
        location=[lat, lon],
        zoom_start=zoom,
        tiles=None,  # Start with no tiles to allow selection
        width=width,
        height=height
    )
    
    # Add multiple basemap options that users can toggle between
    # 1. Satellite imagery (default for this map type)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite Imagery',
        control=True,
    ).add_to(m)
    
    # 2. Dark minimal basemap
    folium.TileLayer(
        tiles="cartodbdark_matter",
        name="Dark Minimal",
        control=True,
    ).add_to(m)
    
    # 3. Light minimal basemap
    folium.TileLayer(
        tiles="cartodbpositron",
        name="Light Minimal",
        control=True,
    ).add_to(m)
    
    # 4. Standard OpenStreetMap
    folium.TileLayer(
        tiles="OpenStreetMap",
        name="Street Map",
        control=True,
    ).add_to(m)
    
    # 5. Topographic full map
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a>',
        name='Topographic Map',
        control=True,
    ).add_to(m)
    
    # Add Topography Lines overlay (can be toggled on/off)
    # Using OpenTopoMap contour lines which are more reliable
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='Map data: &copy; OpenStreetMap contributors, SRTM | Style: &copy; OpenTopoMap',
        name='Topography Lines',
        overlay=True,  # Important: make it an overlay, not a base layer
        opacity=0.6,
        control=True,
    ).add_to(m)
    
    # For satellite view, we'll combine the satellite imagery with place labels directly
    if data_type == "satellite":
        # Always add labels overlay for satellite view without toggle option
        folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png',
            attr='&copy; CartoDB',
            name='_PlaceLabelsHidden',  # Underscore prefix to hide from layer control
            overlay=True,
            opacity=0.9,
            control=False,  # No control, always on for satellite
            show=True,      # Always visible
        ).add_to(m)
        
        # Add coastlines and borders overlay
        folium.TileLayer(
            tiles='https://services.arcgisonline.com/arcgis/rest/services/Ocean/World_Ocean_Reference/MapServer/tile/{z}/{y}/{x}',
            attr='&copy; Esri',
            name='_CoastlinesBordersHidden',  # Underscore prefix to hide from layer control
            overlay=True,
            opacity=0.8,
            control=False,  # No control, always on for satellite
            show=True,      # Always visible
        ).add_to(m)
    else:
        # For non-satellite map types, place labels are toggleable
        folium.TileLayer(
            tiles='https://{s}.basemaps.cartocdn.com/rastertiles/voyager_only_labels/{z}/{x}/{y}{r}.png',
            attr='&copy; CartoDB',
            name='Place Labels',
            overlay=True,  # This makes it an overlay that can be toggled
            opacity=0.9,
            control=True,
        ).add_to(m)
    
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
                               zoom=10, width=800, height=600, style="ethereal"):
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
            lat, lon, zoom=zoom, width=width, height=height, style=palette
        )
    elif data_type == "satellite":
        return create_artistic_satellite_map(
            lat, lon, zoom=zoom, width=width, height=height, style=palette, data_type=data_type
        )
    else:
        # Default to topography
        return create_artistic_topography_map(
            lat, lon, zoom=zoom, width=width, height=height, style=palette
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