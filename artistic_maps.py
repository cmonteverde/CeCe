"""
Artistic Map Module for Climate Copilot

This module provides unique, artistic map visualizations by combining
high-resolution topography, land use, satellite imagery, and custom styling.
The goal is to create visually distinctive maps that stand out from
conventional map services while maintaining scientific accuracy.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.colors import LinearSegmentedColormap
import folium
from folium.plugins import HeatMap
import contextily as cx
import geopandas as gpd
from shapely.geometry import Point, Polygon
import rasterio
from rasterio.plot import show
import rioxarray
import elevation
import os
from io import BytesIO
import base64
from PIL import Image, ImageFilter, ImageEnhance

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

def create_custom_colormap(palette_name):
    """
    Create a custom matplotlib colormap from predefined artistic palettes
    
    Args:
        palette_name: Name of the palette from ARTISTIC_PALETTES
    
    Returns:
        matplotlib colormap
    """
    if palette_name not in ARTISTIC_PALETTES:
        raise ValueError(f"Palette {palette_name} not found. Available palettes: {list(ARTISTIC_PALETTES.keys())}")
    
    colors = ARTISTIC_PALETTES[palette_name]["colors"]
    return LinearSegmentedColormap.from_list(ARTISTIC_PALETTES[palette_name]["name"], colors)

def apply_artistic_effects(image, enhancement_factor=1.2, sharpness=1.5, contrast=1.3):
    """
    Apply artistic effects to an image to create a unique visual style
    
    Args:
        image: PIL Image
        enhancement_factor: Color enhancement factor
        sharpness: Sharpness enhancement factor
        contrast: Contrast enhancement factor
    
    Returns:
        Enhanced PIL Image
    """
    # Convert to PIL Image if it's a numpy array
    if isinstance(image, np.ndarray):
        image = Image.fromarray(np.uint8(image))
    
    # Apply a subtle blur to create a dreamy effect
    image = image.filter(ImageFilter.GaussianBlur(radius=0.5))
    
    # Enhance colors
    enhancer = ImageEnhance.Color(image)
    image = enhancer.enhance(enhancement_factor)
    
    # Enhance sharpness
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(sharpness)
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)
    
    return image

def create_artistic_topography_map(lat, lon, zoom=10, width=800, height=600, 
                                   palette_name="artistic_terrain", artistic_effects=True):
    """
    Create an artistic topographic map centered at the given coordinates
    
    Args:
        lat: Latitude
        lon: Longitude
        zoom: Zoom level (higher values zoom in more)
        width: Image width in pixels
        height: Image height in pixels
        palette_name: Name of the color palette to use
        artistic_effects: Whether to apply artistic enhancements
    
    Returns:
        matplotlib figure with the artistic map
    """
    # Create a GeoDataFrame point for the center location
    point = gpd.GeoDataFrame([Point(lon, lat)], columns=['geometry'], crs="EPSG:4326")
    
    # Convert to web mercator projection (used by most web map providers)
    point = point.to_crs(epsg=3857)
    
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
    
    # Plot the point (invisible, just to set the extent)
    point.plot(ax=ax, alpha=0)
    
    # Set the extent to create a bounding box centered on our point
    # The size of the box depends on the zoom level
    extent_size = 10000 / (zoom / 10)  # Adjust box size based on zoom
    minx, miny, maxx, maxy = [
        point.geometry.x.values[0] - extent_size,
        point.geometry.y.values[0] - extent_size,
        point.geometry.x.values[0] + extent_size,
        point.geometry.y.values[0] + extent_size
    ]
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    
    # Add stylized topographic basemap using contextily
    if artistic_effects:
        # Use terrain tiles with customized styling
        # Note: Stamen providers are no longer available in newer versions
        # Use OpenStreetMap or other available providers
        try:
            # First try CartoDB basemap which is usually available
            cx.add_basemap(
                ax, source=cx.providers.CartoDB.Positron, 
                crs=point.crs.to_string()
            )
        except Exception as e:
            try:
                # Fallback to OpenStreetMap
                cx.add_basemap(
                    ax, source=cx.providers.OpenStreetMap.Mapnik, 
                    crs=point.crs.to_string()
                )
            except Exception as e:
                # If all else fails, use the default basemap
                cx.add_basemap(ax, crs=point.crs.to_string())
    else:
        # Use standard tiles - with fallbacks
        try:
            cx.add_basemap(
                ax, source=cx.providers.OpenStreetMap.Mapnik, 
                crs=point.crs.to_string()
            )
        except Exception as e:
            # Default basemap as last resort
            cx.add_basemap(ax, crs=point.crs.to_string())
    
    # Remove axis to create a cleaner map
    ax.set_axis_off()
    
    # Apply matplotlib style to make it look more artistic
    plt.style.use('dark_background')
    
    if artistic_effects:
        # Get the image data from the matplotlib figure
        fig.canvas.draw()
        img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        
        # Apply artistic effects
        enhanced_img = apply_artistic_effects(img)
        
        # Create a new figure with the enhanced image
        fig_enhanced = plt.figure(figsize=(width/100, height/100), dpi=100)
        plt.imshow(enhanced_img)
        plt.axis('off')
        return fig_enhanced
    
    return fig

def create_mixed_satellite_map(lat, lon, zoom=10, width=800, height=600, 
                              palette_name="climate_ethereal", artistic_effects=True):
    """
    Create an artistic map that combines satellite imagery with stylized overlays
    
    Args:
        lat: Latitude
        lon: Longitude
        zoom: Zoom level
        width: Image width in pixels
        height: Image height in pixels
        palette_name: Name of the color palette to use
        artistic_effects: Whether to apply artistic enhancements
    
    Returns:
        matplotlib figure with the mixed satellite artistic map
    """
    # Create a figure and axis
    fig, ax = plt.subplots(figsize=(width/100, height/100), dpi=100)
    
    # Create a point GeoDataFrame for the center location
    point = gpd.GeoDataFrame([Point(lon, lat)], columns=['geometry'], crs="EPSG:4326")
    point = point.to_crs(epsg=3857)  # Convert to web mercator
    
    # Set the map extent
    extent_size = 10000 / (zoom / 10)
    minx, miny, maxx, maxy = [
        point.geometry.x.values[0] - extent_size,
        point.geometry.y.values[0] - extent_size,
        point.geometry.x.values[0] + extent_size,
        point.geometry.y.values[0] + extent_size
    ]
    ax.set_xlim(minx, maxx)
    ax.set_ylim(miny, maxy)
    
    # Add satellite imagery base layer
    try:
        # Try to use Esri WorldImagery
        cx.add_basemap(
            ax, source=cx.providers.Esri.WorldImagery,
            crs=point.crs.to_string()
        )
    except Exception as e:
        try:
            # Fallback to another provider
            cx.add_basemap(
                ax, source=cx.providers.OpenStreetMap.Mapnik,
                crs=point.crs.to_string()
            )
        except Exception as e:
            # Last resort: use default basemap
            cx.add_basemap(
                ax, crs=point.crs.to_string()
            )
    
    # Apply semi-transparent topographic overlay with custom styling for an artistic effect
    # Here we're simulating a styled topographic overlay
    if artistic_effects:
        # Create a rectangular overlay for artistic effect
        rect = plt.Rectangle((minx, miny), maxx-minx, maxy-miny, 
                            color=ARTISTIC_PALETTES[palette_name]["colors"][0],
                            alpha=0.3)
        ax.add_patch(rect)
    
    # Remove axis
    ax.set_axis_off()
    
    if artistic_effects:
        # Get the image data
        fig.canvas.draw()
        img = np.frombuffer(fig.canvas.tostring_rgb(), dtype=np.uint8)
        img = img.reshape(fig.canvas.get_width_height()[::-1] + (3,))
        
        # Apply artistic effects with different parameters for satellite imagery
        enhanced_img = apply_artistic_effects(img, enhancement_factor=1.4, 
                                            sharpness=1.3, contrast=1.5)
        
        # Create a new figure with the enhanced image
        fig_enhanced = plt.figure(figsize=(width/100, height/100), dpi=100)
        plt.imshow(enhanced_img)
        plt.axis('off')
        return fig_enhanced
    
    return fig

def create_stylized_folium_map(lat, lon, zoom=10, tiles="cartodbpositron", 
                              width=800, height=600, overlay_type=None):
    """
    Create a stylized interactive Folium map with custom overlay
    
    Args:
        lat: Latitude
        lon: Longitude
        zoom: Initial zoom level
        tiles: Base tile layer (e.g., "cartodbpositron", "cartodbdark_matter")
        width: Map width in pixels
        height: Map height in pixels
        overlay_type: Type of overlay to add (None, "topography", "landuse", "satellite")
    
    Returns:
        Folium map with stylized layers
    """
    # Create a base map with a stylish tile layer
    m = folium.Map(
        location=[lat, lon],
        zoom_start=zoom,
        tiles=tiles,
        width=width,
        height=height
    )
    
    # Add attribution
    attribution = 'Map styles by Climate Copilot | Data © OpenStreetMap contributors, SRTM'
    m.get_root().html.add_child(folium.Element(f'''
        <div style="position: fixed; bottom: 10px; left: 10px; z-index: 1000; 
                  background-color: rgba(255, 255, 255, 0.7); padding: 5px; border-radius: 5px;
                  font-size: 10px; font-family: Arial;">
            {attribution}
        </div>
    '''))
    
    # Add custom overlays based on the selected type
    if overlay_type == "topography":
        # Add a WMS layer for topography (SRTM)
        folium.WmsTileLayer(
            url="http://ows.mundialis.de/services/service?",
            layers="SRTM30-Colored-Hillshade",
            transparent=True,
            overlay=True,
            name="Topography",
            fmt="image/png",
            opacity=0.7
        ).add_to(m)
    
    elif overlay_type == "landuse":
        # Add a WMS layer for land cover/land use
        folium.WmsTileLayer(
            url="https://maps.isric.org/mapserv?map=/map/wrb.map",
            layers="wrb",
            transparent=True,
            overlay=True,
            name="Land Use",
            fmt="image/png",
            opacity=0.7
        ).add_to(m)
    
    elif overlay_type == "satellite":
        # Add a tile layer for satellite imagery
        folium.TileLayer(
            tiles="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            attr="Esri",
            name="Satellite",
            overlay=True,
            opacity=0.7
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add a scale bar
    folium.plugins.MeasureControl(position='bottomleft', primary_length_unit='meters').add_to(m)
    
    # Add a mini map for context
    folium.plugins.MiniMap(toggle_display=True).add_to(m)
    
    # Add a fullscreen button
    folium.plugins.Fullscreen(position='topleft').add_to(m)
    
    return m

def matplotlib_to_folium(fig, m, bounds=None):
    """
    Convert a matplotlib figure to a Folium overlay
    
    Args:
        fig: matplotlib figure
        m: folium map
        bounds: geographic bounds [min_lon, min_lat, max_lon, max_lat]
    
    Returns:
        Folium map with the matplotlib figure as an overlay
    """
    # Save the figure to a BytesIO object
    img_data = BytesIO()
    fig.savefig(img_data, format='png', bbox_inches='tight', pad_inches=0)
    img_data.seek(0)
    
    # Encode the image as base64
    encoded = base64.b64encode(img_data.read()).decode('utf-8')
    
    # Add the image as an overlay to the folium map
    if bounds:
        folium.raster_layers.ImageOverlay(
            image=f"data:image/png;base64,{encoded}",
            bounds=bounds,
            opacity=0.7,
            name="Artistic Layer"
        ).add_to(m)
    
    return m

def create_artistic_climate_map(lat, lon, data=None, data_type="temperature", 
                               zoom=10, width=800, height=600, style="ethereal"):
    """
    Create an artistic climate map with the specified data overlay
    
    Args:
        lat: Latitude
        lon: Longitude
        data: Climate data to overlay
        data_type: Type of climate data ("temperature", "precipitation", etc.)
        zoom: Zoom level
        width: Map width in pixels
        height: Map height in pixels
        style: Artistic style to apply ("ethereal", "dramatic", "moody", etc.)
    
    Returns:
        Folium map with artistic climate visualization
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
    
    # Create a base folium map with a stylish dark tile layer
    m = folium.Map(
        location=[lat, lon],
        zoom_start=zoom,
        tiles="cartodbdark_matter",
        width=width,
        height=height
    )
    
    # Create artistic overlay based on data type
    if data_type == "topography":
        # Create artistic topographic map
        fig = create_artistic_topography_map(
            lat, lon, zoom=zoom, width=width, height=height,
            palette_name=palette, artistic_effects=True
        )
        
        # Calculate bounds (approximate)
        deg_span = 0.05 * (15 / zoom)  # Adjust based on zoom level
        bounds = [lon - deg_span, lat - deg_span, lon + deg_span, lat + deg_span]
        
        # Add as overlay
        m = matplotlib_to_folium(fig, m, bounds)
        plt.close(fig)  # Close the figure to free memory
        
    elif data_type == "satellite":
        # Create artistic satellite map
        fig = create_mixed_satellite_map(
            lat, lon, zoom=zoom, width=width, height=height,
            palette_name=palette, artistic_effects=True
        )
        
        # Calculate bounds (approximate)
        deg_span = 0.05 * (15 / zoom)
        bounds = [lon - deg_span, lat - deg_span, lon + deg_span, lat + deg_span]
        
        # Add as overlay
        m = matplotlib_to_folium(fig, m, bounds)
        plt.close(fig)
    
    elif data is not None:
        # If we have actual climate data, create a custom visualization
        # This is a placeholder for adding actual climate data overlays
        # We would need to define the specific data structure and visualization method
        pass
    
    # Add layer control and other UI elements
    folium.LayerControl().add_to(m)
    folium.plugins.MiniMap(toggle_display=True).add_to(m)
    folium.plugins.Fullscreen(position='topleft').add_to(m)
    
    # Add attribution
    attribution = f'Climate Copilot Artistic {style.capitalize()} Style | Data © OpenStreetMap contributors'
    m.get_root().html.add_child(folium.Element(f'''
        <div style="position: fixed; bottom: 10px; left: 10px; z-index: 1000; 
                  background-color: rgba(0, 0, 0, 0.7); padding: 5px; border-radius: 5px;
                  font-size: 10px; font-family: Arial; color: white;">
            {attribution}
        </div>
    '''))
    
    return m

# Custom styling functions for map elements

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

def create_custom_legend(m, title, items):
    """
    Add a custom stylized legend to a folium map
    
    Args:
        m: Folium map
        title: Legend title
        items: List of (color, label) tuples
    
    Returns:
        Folium map with custom legend
    """
    legend_html = f'''
    <div style="position: fixed; bottom: 50px; right: 50px; z-index: 1000; 
              background-color: rgba(0, 0, 0, 0.7); padding: 10px; border-radius: 8px;
              font-size: 12px; font-family: 'Helvetica Neue', Arial; color: white;
              box-shadow: 0 0 15px rgba(0,0,0,0.2);">
        <div style="margin-bottom: 5px; font-weight: bold; font-size: 14px; text-align: center;">
            {title}
        </div>
    '''
    
    for color, label in items:
        legend_html += f'''
        <div style="display: flex; align-items: center; margin-bottom: 3px;">
            <div style="background-color: {color}; width: 15px; height: 15px; margin-right: 5px;"></div>
            <div>{label}</div>
        </div>
        '''
    
    legend_html += '</div>'
    m.get_root().html.add_child(folium.Element(legend_html))
    
    return m