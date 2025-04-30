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
    # Create base map
    m = folium.Map(
        location=[lat, lon],
        zoom_start=zoom,
        tiles="cartodbdark_matter",
        width=width,
        height=height
    )
    
    # Add some artistic elements based on the palette
    if style in ARTISTIC_PALETTES:
        palette = ARTISTIC_PALETTES[style]
        colors = palette["colors"]
        
        # Add artistic elements - circles with palette colors
        for i in range(10):
            # Create random offsets within view
            lat_offset = (random.random() - 0.5) * 0.05
            lon_offset = (random.random() - 0.5) * 0.05
            
            # Get random color from palette
            color = colors[i % len(colors)]
            
            # Random radius and opacity for variety
            radius = random.randint(500, 2000)
            opacity = random.uniform(0.2, 0.5)
            
            # Add circle
            folium.Circle(
                location=[lat + lat_offset, lon + lon_offset],
                radius=radius,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=opacity,
                opacity=opacity * 0.8
            ).add_to(m)
    
    # Add a topographic overlay for terrain effect
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='Map data: &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, <a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; <a href="https://opentopomap.org">OpenTopoMap</a>',
        name='Topography',
        overlay=True,
        opacity=0.7
    ).add_to(m)
    
    # Add a minimap for context
    minimap = MiniMap(toggle_display=True, position='bottomright')
    m.add_child(minimap)
    
    # Add fullscreen control
    Fullscreen(position='topleft').add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
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

def create_artistic_satellite_map(lat, lon, zoom=10, width=800, height=600, style="climate_ethereal"):
    """
    Create an artistic map based on satellite imagery
    
    Args:
        lat: Latitude
        lon: Longitude
        zoom: Zoom level
        width: Image width in pixels
        height: Image height in pixels
        style: Style name from ARTISTIC_PALETTES
    
    Returns:
        Folium map with artistic satellite imagery
    """
    # Create base map with satellite imagery
    m = folium.Map(
        location=[lat, lon],
        zoom_start=zoom,
        tiles="cartodbdark_matter",
        width=width,
        height=height
    )
    
    # Add satellite base layer
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite Imagery',
        overlay=False
    ).add_to(m)
    
    # Add artistic elements based on the palette
    if style in ARTISTIC_PALETTES:
        palette = ARTISTIC_PALETTES[style]
        colors = palette["colors"]
        
        # Create semi-transparent gradient overlay for artistic effect
        gradient = {}
        for i, color in enumerate(colors):
            # Create normalized gradient stops
            position = f"{i / (len(colors) - 1):.1f}"
            gradient[position] = color
        
        # Add a heatmap with very low intensity but using our palette colors for a gradient effect
        # This creates a colored overlay effect without real data
        # Generate some random points around the center to create a gradient
        points = []
        for i in range(20):
            lat_offset = (random.random() - 0.5) * 0.1
            lon_offset = (random.random() - 0.5) * 0.1
            # Weight increases toward center for a focal point
            weight = 1.0 - (abs(lat_offset) + abs(lon_offset)) * 5
            points.append([lat + lat_offset, lon + lon_offset, weight])
        
        # Add the heatmap as an artistic overlay
        HeatMap(
            points,
            radius=25,
            gradient=gradient,
            min_opacity=0.3,
            blur=20,
            max_zoom=zoom+2,
            name="Artistic Overlay"
        ).add_to(m)
    
    # Add a minimap
    minimap = MiniMap(toggle_display=True, position='bottomright')
    m.add_child(minimap)
    
    # Add fullscreen control
    Fullscreen(position='topleft').add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
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
            lat, lon, zoom=zoom, width=width, height=height, style=palette
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