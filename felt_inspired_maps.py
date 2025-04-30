"""
Felt-Inspired Map Module for Climate Copilot

This module provides a modern, interactive map experience inspired by Felt.com,
with enhanced data visualization capabilities for climate data.

Features:
- Modern, clean UI with minimalist controls
- Multiple high-quality basemaps
- Interactive data layers with smooth transitions
- Enhanced data visualization for climate metrics
- Collaborative annotation capabilities
- High-performance rendering
"""

import streamlit as st
import folium
from folium.plugins import HeatMap, MiniMap, Fullscreen, MarkerCluster, Draw, TimestampedGeoJson
from folium.plugins import FloatImage, MeasureControl, MousePosition, Geocoder
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.colors import LinearSegmentedColormap, to_hex
import io
import base64
from PIL import Image
import requests
import json
import srtm_elevation
import nasa_ee_elevation
import branca.colormap as bcm
import tempfile
import os

# Enhanced color palettes inspired by Felt's modern aesthetic
FELT_PALETTES = {
    "terrain": {
        "name": "Terrain",
        "description": "Modern terrain visualization with subtle elevation shading",
        "colors": ["#f9f9f7", "#e8e8e3", "#d5d2c3", "#b7b5a5", "#9b9988", "#7e7c6d", "#63625c", "#505050"],
    },
    "satellite": {
        "name": "Satellite",
        "description": "Vibrant satellite imagery enhanced for clarity",
        "colors": ["#0f0f14", "#242439", "#313a56", "#455773", "#5a7490", "#7596ad", "#94bbc9", "#bfe0e4"],
    },
    "temperature": {
        "name": "Temperature",
        "description": "Modern temperature gradient inspired by scientific visualization",
        "colors": ["#053061", "#2166ac", "#4393c3", "#92c5de", "#fddbc7", "#f4a582", "#d6604d", "#b2182b", "#67001f"],
    },
    "precipitation": {
        "name": "Precipitation",
        "description": "Contemporary precipitation visualization with modern blues",
        "colors": ["#FFFFFF", "#F2F2F2", "#D4E6F1", "#A9CCE3", "#7FB3D5", "#5499C7", "#2980B9", "#1F618D", "#154360"],
    },
    "green": {
        "name": "Vegetation",
        "description": "Modern vegetation gradient for land use visualization",
        "colors": ["#edf8fb", "#ccece6", "#99d8c9", "#66c2a4", "#41ae76", "#238b45", "#006d2c", "#00441b"],
    },
    "urban": {
        "name": "Urban",
        "description": "Muted urban palette for human-centered visualizations",
        "colors": ["#f7f7f7", "#d9d9d9", "#bdbdbd", "#969696", "#737373", "#525252", "#252525"],
    },
    "elevation": {
        "name": "Elevation",
        "description": "Sophisticated elevation gradient for topographic analysis",
        "colors": ["#ffffd4", "#fee391", "#fec44f", "#fe9929", "#ec7014", "#cc4c02", "#8c2d04"],
    }
}

# Define map tile sources with modern aesthetics
MAP_TILES = {
    "light": {
        "name": "Light",
        "url": "https://basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        "attribution": "© CartoDB",
        "style": "light",
    },
    "dark": {
        "name": "Dark",
        "url": "https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        "attribution": "© CartoDB",
        "style": "dark",
    },
    "outdoors": {
        "name": "Outdoors",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        "attribution": "© Esri",
        "style": "light",
    },
    "satellite": {
        "name": "Satellite",
        "url": "https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        "attribution": "© Google",
        "style": "dark",
    },
    "terrain": {
        "name": "Terrain",
        "url": "https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}",
        "attribution": "© Google",
        "style": "light",
    },
    "hybrid": {
        "name": "Hybrid",
        "url": "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
        "attribution": "© Google",
        "style": "dark",
    },
    "topo": {
        "name": "Topographic",
        "url": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
        "attribution": "© Esri",
        "style": "light",
    },
    "street": {
        "name": "Street",
        "url": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        "attribution": "© OpenStreetMap",
        "style": "light",
    },
    "watercolor": {
        "name": "Watercolor",
        "url": "https://stamen-tiles-{s}.a.ssl.fastly.net/watercolor/{z}/{x}/{y}.jpg",
        "attribution": "© Stamen",
        "style": "light",
    },
}

class FeltMap:
    """Felt-inspired interactive map for Climate Copilot"""
    
    def __init__(self, lat=37.7749, lon=-122.4194, zoom=10, width="100%", height=600, 
                tiles="light", style="modern", show_toolbar=True):
        """
        Initialize Felt-inspired map
        
        Args:
            lat: Latitude for map center
            lon: Longitude for map center
            zoom: Initial zoom level
            width: Map width
            height: Map height
            tiles: Map tile source ("light", "dark", "outdoors", etc.)
            style: UI style ("modern", "minimal", "detailed")
            show_toolbar: Whether to show the toolbar
        """
        self.lat = lat
        self.lon = lon
        self.zoom = zoom
        self.width = width
        self.height = height
        self.tile_source = tiles if tiles in MAP_TILES else "light"
        self.style = style
        self.show_toolbar = show_toolbar
        self.layers = []
        self.overlays = []
        
        # Create the base map
        self.create_base_map()
        
    def create_base_map(self):
        """Create the base Folium map with Felt-inspired styling"""
        tile_info = MAP_TILES[self.tile_source]
        
        # Create map with basic settings
        self.map = folium.Map(
            location=[self.lat, self.lon],
            zoom_start=self.zoom,
            min_zoom=2,
            max_zoom=19,
            tiles=None,  # We'll add custom tile layers
            width=self.width,
            height=self.height,
            control_scale=True,
            prefer_canvas=True,
            zoom_control=False  # We'll add custom zoom control later
        )
        
        # Add base tile layer
        folium.TileLayer(
            tiles=tile_info["url"],
            attr=tile_info["attribution"],
            name=tile_info["name"],
            overlay=False,
            control=True
        ).add_to(self.map)
        
        # Add additional tile options
        for key, tile in MAP_TILES.items():
            if key != self.tile_source:
                folium.TileLayer(
                    tiles=tile["url"],
                    attr=tile["attribution"],
                    name=tile["name"],
                    overlay=False,
                    control=True
                ).add_to(self.map)
        
        # Add modern controls
        if self.show_toolbar:
            # Add fullscreen control
            Fullscreen(
                position="topright",
                title="Expand map",
                title_cancel="Exit fullscreen",
                force_separate_button=True
            ).add_to(self.map)
            
            # Add measure tool for distances and areas
            MeasureControl(
                position="topright",
                primary_length_unit="kilometers",
                secondary_length_unit="miles",
                primary_area_unit="square kilometers",
                secondary_area_unit="acres"
            ).add_to(self.map)
            
            # Add drawing tools
            Draw(
                position="topright",
                draw_options={
                    "polyline": {"allowIntersection": False},
                    "polygon": {"allowIntersection": False},
                    "circle": True,
                    "rectangle": True,
                    "marker": True,
                    "circlemarker": False,
                },
                edit_options={
                    "poly": {"allowIntersection": False}
                }
            ).add_to(self.map)
            
            # Add geocoder for location search
            Geocoder(
                position="topleft",
                add_marker=True
            ).add_to(self.map)
            
            # Add mouse position display
            MousePosition(
                position="bottomright",
                separator=" | ",
                empty_string="",
                lng_first=True,
                num_digits=5,
                prefix="Coordinates: "
            ).add_to(self.map)
            
            # Add mini map
            minimap = MiniMap(
                position="bottomright",
                toggle_display=True,
                tile_layer=tile_info["url"],
                zoom_level_offset=-6,
                width=150,
                height=150
            )
            self.map.add_child(minimap)
        
        # Add layer control
        folium.LayerControl(position="topright", collapsed=False).add_to(self.map)
        
        # Apply modern styling
        self.apply_felt_styling()
    
    def apply_felt_styling(self):
        """Apply Felt-inspired CSS styling to the map"""
        # Define the CSS based on style
        if self.style == "modern":
            css = """
            <style>
                .leaflet-container { 
                    background: #f8f9fa; 
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                }
                .leaflet-control-zoom, .leaflet-control-layers {
                    border: none !important;
                    border-radius: 8px !important;
                    overflow: hidden !important;
                    box-shadow: 0 1px 5px rgba(0,0,0,0.1) !important;
                }
                .leaflet-control-zoom a, .leaflet-control-layers-toggle {
                    background-color: white !important;
                    color: #555 !important;
                    transition: all 0.2s ease !important;
                }
                .leaflet-control-zoom a:hover, .leaflet-control-layers-toggle:hover {
                    background-color: #f8f9fa !important;
                    color: #333 !important;
                }
                .leaflet-control-attribution {
                    background-color: rgba(255, 255, 255, 0.7) !important;
                    font-size: 10px !important;
                    color: #777 !important;
                }
                .leaflet-popup-content-wrapper {
                    border-radius: 8px !important;
                    box-shadow: 0 3px 14px rgba(0,0,0,0.1) !important;
                }
                .leaflet-popup-content {
                    margin: 12px 20px !important;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
                }
                .leaflet-popup-tip {
                    box-shadow: 0 3px 14px rgba(0,0,0,0.1) !important;
                }
                /* Custom styling for control panels */
                .leaflet-control-layers-expanded {
                    padding: 10px !important;
                    background-color: white !important;
                    border-radius: 8px !important;
                    box-shadow: 0 1px 5px rgba(0,0,0,0.1) !important;
                }
                .leaflet-control-layers-list {
                    margin-bottom: 0 !important;
                }
                .leaflet-control-layers-selector {
                    margin-right: 6px !important;
                }
                /* Custom tooltip styling */
                .leaflet-tooltip {
                    background-color: white !important;
                    border: none !important;
                    border-radius: 4px !important;
                    color: #333 !important;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
                }
                .leaflet-tooltip-top:before,
                .leaflet-tooltip-bottom:before,
                .leaflet-tooltip-left:before,
                .leaflet-tooltip-right:before {
                    border: none !important;
                }
                /* Custom drawing tools styling */
                .leaflet-draw-toolbar a {
                    background-color: white !important;
                    border-radius: 4px !important;
                    margin-bottom: 5px !important;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
                }
                .leaflet-draw-toolbar a:hover {
                    background-color: #f8f9fa !important;
                }
                .leaflet-draw-tooltip {
                    background-color: rgba(0, 0, 0, 0.7) !important;
                    border: none !important;
                    border-radius: 4px !important;
                    color: white !important;
                }
                /* Custom map overlay styling */
                .map-overlay {
                    position: absolute;
                    bottom: 20px;
                    left: 20px;
                    z-index: 1000;
                    background-color: rgba(255, 255, 255, 0.9);
                    padding: 10px 15px;
                    border-radius: 8px;
                    box-shadow: 0 1px 5px rgba(0,0,0,0.1);
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                    font-size: 12px;
                    color: #555;
                    max-width: 250px;
                }
                .map-overlay h3 {
                    margin: 0 0 5px 0;
                    font-size: 14px;
                    font-weight: 600;
                    color: #333;
                }
                .map-overlay p {
                    margin: 0;
                    line-height: 1.4;
                }
            </style>
            """
        elif self.style == "minimal":
            css = """
            <style>
                .leaflet-container { 
                    background: #ffffff; 
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                }
                .leaflet-control-zoom, .leaflet-control-layers {
                    opacity: 0.6;
                    transition: opacity 0.3s ease;
                    border: none !important;
                    border-radius: 4px !important;
                }
                .leaflet-control-zoom:hover, .leaflet-control-layers:hover {
                    opacity: 1;
                }
                .leaflet-control-attribution {
                    background-color: transparent !important;
                    font-size: 9px !important;
                    color: #999 !important;
                }
                .leaflet-popup-content-wrapper {
                    border-radius: 4px !important;
                }
                .leaflet-popup-content {
                    margin: 10px 15px !important;
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif !important;
                    font-size: 12px !important;
                }
                .leaflet-control-layers-expanded {
                    padding: 8px !important;
                    background-color: white !important;
                    border-radius: 4px !important;
                }
            </style>
            """
        else:  # default or "detailed"
            css = """
            <style>
                .leaflet-container { 
                    background: #f0f0f0; 
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
                }
                .leaflet-control-zoom, .leaflet-control-layers {
                    border-radius: 4px !important;
                }
                .leaflet-control-attribution {
                    font-size: 10px !important;
                }
            </style>
            """
        
        # Add CSS to map
        self.map.get_root().html.add_child(folium.Element(css))
        
        # Add attribution
        attribution = 'Climate Copilot Map | Inspired by <a href="https://felt.com" target="_blank">Felt</a>'
        self.map.get_root().html.add_child(folium.Element(f"""
            <div style="position: fixed; bottom: 10px; left: 10px; z-index: 1000; 
                      background-color: rgba(255, 255, 255, 0.7); padding: 5px 8px; border-radius: 4px;
                      font-size: 10px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #555;">
                {attribution}
            </div>
        """))

    def add_elevation_contours(self, color="#6644aa", weight=1.5, num_contours=15, 
                              use_feet=False, opacity=0.7, name="Elevation Contours"):
        """
        Add elevation contours to the map with Felt-like aesthetic
        
        Args:
            color: Contour line color
            weight: Line weight
            num_contours: Number of contour lines
            use_feet: Whether to use feet instead of meters
            opacity: Line opacity
            name: Layer name for the control panel
        """
        # Define contour dimensions based on zoom
        contour_width = 100 if self.zoom > 12 else 80
        contour_height = 100 if self.zoom > 12 else 80
        
        try:
            # Fetch elevation data with NASA Earth Explorer credentials
            print(f"Fetching elevation data for contours at {self.lat}, {self.lon}")
            elevation_data, bounds = nasa_ee_elevation.fetch_elevation_data(
                lat=self.lat,
                lon=self.lon,
                width=contour_width,
                height=contour_height,
                radius=0.05
            )
            
            # If NASA Earth Explorer fails, try SRTM data
            if elevation_data is None:
                print("NASA Earth Explorer failed, trying SRTM data")
                elevation_data, bounds = srtm_elevation.fetch_elevation_array(
                    lat=self.lat,
                    lon=self.lon,
                    width=contour_width,
                    height=contour_height,
                    radius=0.05
                )
            
            if elevation_data is None:
                print("Both elevation data sources failed")
                return self.map
            
            # Generate contour lines
            min_elevation = np.nanmin(elevation_data)
            max_elevation = np.nanmax(elevation_data)
            
            # Convert to feet if requested
            if use_feet:
                # 1 meter = 3.28084 feet
                elevation_data = elevation_data * 3.28084
                min_elevation = min_elevation * 3.28084
                max_elevation = max_elevation * 3.28084
                unit = "ft"
            else:
                unit = "m"
            
            # Create levels for contour lines with a nice distribution
            # Use a logarithmic scale for better visualization of varying terrain
            if max_elevation - min_elevation > 1000:
                # For mountainous terrain, use log-scale
                levels = np.geomspace(
                    max(1, min_elevation), 
                    max_elevation, 
                    num=num_contours
                )
                # Round to nice numbers
                levels = np.array([round(x/10)*10 for x in levels])
            else:
                # For flatter areas, use linear scale with a minimum step
                step = max(5, (max_elevation - min_elevation) / num_contours)
                levels = np.arange(
                    min_elevation, 
                    max_elevation + step, 
                    step
                )
            
            # Remove duplicates and sort
            levels = np.unique(levels)
            
            # Create meshgrid for plotting
            minx, miny, maxx, maxy = bounds
            x = np.linspace(minx, maxx, contour_width)
            y = np.linspace(miny, maxy, contour_height)
            X, Y = np.meshgrid(x, y)
            
            # Create feature group for contours
            contour_group = folium.FeatureGroup(name=f"{name} ({unit})", overlay=True, control=True)
            
            # Generate contours with a smoother algorithm
            for level in levels:
                try:
                    # Use matplotlib to compute contours
                    fig, ax = plt.subplots(figsize=(8, 6))
                    contour = ax.contour(X, Y, elevation_data, levels=[level], colors='black')
                    plt.close(fig)
                    
                    # Extract contour paths
                    contour_paths = []
                    for path_collection in contour.collections:
                        for path in path_collection.get_paths():
                            if len(path.vertices) > 1:  # Only if we have at least 2 points
                                # Convert to lat, lon and add to paths
                                contour_points = [(y, x) for x, y in path.vertices]
                                contour_paths.append(contour_points)
                    
                    # Add each path as a separate line
                    for contour_path in contour_paths:
                        folium.PolyLine(
                            locations=contour_path,
                            color=color,
                            weight=weight,
                            opacity=opacity,
                            tooltip=f"Elevation: {int(level)} {unit}",
                            smooth_factor=1.5,
                            dash_array='5, 5' if level % 2 == 0 else None,
                        ).add_to(contour_group)
                except Exception as e:
                    print(f"Error creating contour at level {level}: {e}")
            
            # Add the contour group to the map
            contour_group.add_to(self.map)
            
            # Store overlay reference
            self.overlays.append({"name": name, "group": contour_group})
            
            return self.map
            
        except Exception as e:
            print(f"Failed to add contour lines: {e}")
            return self.map

    def add_temperature_layer(self, data, min_temp=None, max_temp=None, radius=10, 
                             blur=15, name="Temperature", palette="temperature"):
        """
        Add temperature data visualization layer
        
        Args:
            data: List of (lat, lon, temp) tuples
            min_temp: Minimum temperature value (auto if None)
            max_temp: Maximum temperature value (auto if None)
            radius: Heat point radius
            blur: Heat point blur radius
            name: Layer name
            palette: Color palette from FELT_PALETTES
        """
        if not data:
            print("No temperature data provided")
            return self.map
        
        # Extract data points
        data_points = [(lat, lon, temp) for lat, lon, temp in data]
        
        # Determine min/max if not provided
        if min_temp is None:
            min_temp = min([temp for _, _, temp in data_points])
        if max_temp is None:
            max_temp = max([temp for _, _, temp in data_points])
        
        # Get palette colors
        if palette in FELT_PALETTES:
            colors = FELT_PALETTES[palette]["colors"]
        else:
            colors = FELT_PALETTES["temperature"]["colors"]
        
        # Create a gradient color map using the palette
        color_map = bcm.LinearColormap(
            colors=colors,
            vmin=min_temp,
            vmax=max_temp,
            caption=f'Temperature (°C)'
        )
        
        # Add the heatmap layer
        heat_data = [[lat, lon, temp] for lat, lon, temp in data_points]
        heatmap = HeatMap(
            heat_data,
            min_opacity=0.3,
            max_opacity=0.8,
            radius=radius,
            blur=blur,
            gradient={0.0: colors[0], 0.5: colors[len(colors)//2], 1.0: colors[-1]},
            name=name
        )
        
        # Create feature group for the layer
        fg = folium.FeatureGroup(name=name)
        heatmap.add_to(fg)
        
        # Add color scale to the map
        color_map.add_to(self.map)
        
        # Add the feature group to the map
        fg.add_to(self.map)
        
        # Store layer reference
        self.layers.append({"name": name, "group": fg})
        
        return self.map
    
    def add_precipitation_layer(self, data, min_precip=None, max_precip=None, 
                               name="Precipitation", palette="precipitation"):
        """
        Add precipitation data visualization layer using custom gradient overlay
        
        Args:
            data: Dict of {(lat, lon): precip_value} or list of (lat, lon, precip) tuples
            min_precip: Minimum precipitation value (auto if None)
            max_precip: Maximum precipitation value (auto if None)
            name: Layer name
            palette: Color palette from FELT_PALETTES
        """
        # Convert data to list of tuples if needed
        if isinstance(data, dict):
            data_points = [(lat, lon, precip) for (lat, lon), precip in data.items()]
        else:
            data_points = data
        
        if not data_points:
            print("No precipitation data provided")
            return self.map
        
        # Determine min/max if not provided
        if min_precip is None:
            min_precip = min([precip for _, _, precip in data_points])
        if max_precip is None:
            max_precip = max([precip for _, _, precip in data_points])
        
        # Get palette colors
        if palette in FELT_PALETTES:
            colors = FELT_PALETTES[palette]["colors"]
        else:
            colors = FELT_PALETTES["precipitation"]["colors"]
        
        # Create feature group for the layer
        fg = folium.FeatureGroup(name=name)
        
        # Create a color map
        color_map = bcm.LinearColormap(
            colors=colors,
            vmin=min_precip,
            vmax=max_precip,
            caption=f'Precipitation (mm)'
        )
        
        # Add the color map to the map
        color_map.add_to(self.map)
        
        # Create grid markers with colored circles for precipitation
        for lat, lon, precip in data_points:
            # Skip points with no precipitation
            if precip <= 0:
                continue
                
            # Scale the circle radius based on precipitation amount (non-linear scale)
            radius = min(20, max(5, 5 * (precip / max_precip) ** 0.5 * 20))
            
            # Get color from the colormap
            if precip < min_precip:
                color = colors[0]
            elif precip > max_precip:
                color = colors[-1]
            else:
                normalized = (precip - min_precip) / (max_precip - min_precip)
                color_idx = int(normalized * (len(colors) - 1))
                color = colors[color_idx]
            
            # Add a circle marker
            folium.CircleMarker(
                location=[lat, lon],
                radius=radius,
                color=None,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                tooltip=f"Precipitation: {precip:.1f} mm"
            ).add_to(fg)
        
        # Add the feature group to the map
        fg.add_to(self.map)
        
        # Store layer reference
        self.layers.append({"name": name, "group": fg})
        
        return self.map
    
    def add_climate_risk_layer(self, risk_data, name="Climate Risk", palette="urban"):
        """
        Add climate risk visualization layer
        
        Args:
            risk_data: List of (lat, lon, geojson_polygon, risk_level, risk_type) tuples
            name: Layer name
            palette: Color palette from FELT_PALETTES
        """
        if not risk_data:
            print("No risk data provided")
            return self.map
        
        # Get palette colors
        if palette in FELT_PALETTES:
            colors = FELT_PALETTES[palette]["colors"]
        else:
            colors = FELT_PALETTES["urban"]["colors"]
        
        # Create feature group for the layer
        fg = folium.FeatureGroup(name=name)
        
        # Define risk level colors
        risk_colors = {
            "very low": colors[0],
            "low": colors[1],
            "moderate": colors[2],
            "high": colors[3],
            "very high": colors[4],
            "extreme": colors[-1]
        }
        
        # Add risk areas
        for lat, lon, geojson_polygon, risk_level, risk_type in risk_data:
            # Convert risk level to lowercase string for matching
            risk_level_str = str(risk_level).lower()
            
            # Get color for risk level
            if risk_level_str in risk_colors:
                color = risk_colors[risk_level_str]
            else:
                # Use a gradient based on numeric risk level if available
                try:
                    risk_num = float(risk_level)
                    normalized = min(1.0, max(0.0, risk_num / 5.0))  # Assuming 0-5 scale
                    color_idx = int(normalized * (len(colors) - 1))
                    color = colors[color_idx]
                except (ValueError, TypeError):
                    # Default to moderate risk color
                    color = risk_colors["moderate"]
            
            # Add the risk area as a GeoJSON polygon
            if geojson_polygon:
                folium.GeoJson(
                    geojson_polygon,
                    style_function=lambda x, color=color: {
                        'fillColor': color,
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0.6
                    },
                    tooltip=f"{risk_type}: {risk_level}"
                ).add_to(fg)
            else:
                # If no polygon, use circle marker at the point
                folium.CircleMarker(
                    location=[lat, lon],
                    radius=30,
                    color='black',
                    weight=1,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.6,
                    tooltip=f"{risk_type}: {risk_level}"
                ).add_to(fg)
        
        # Add legend
        legend_html = """
        <div style="position: fixed; bottom: 50px; right: 50px; width: 180px; height: auto; 
                   background-color: white; border-radius: 5px; box-shadow: 0 0 15px rgba(0,0,0,0.1);
                   font-family: Arial; padding: 10px; font-size: 12px; z-index: 9999;">
            <div style="font-weight: bold; margin-bottom: 10px;">Climate Risk Levels</div>
        """
        
        for risk, color in risk_colors.items():
            legend_html += f"""
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: {color}; width: 15px; height: 15px; 
                         border-radius: 3px; margin-right: 5px;"></div>
                <div>{risk.title()}</div>
            </div>
            """
        
        legend_html += "</div>"
        
        # Add the legend HTML as a macro element
        macro = folium.MacroElement().add_to(self.map)
        macro._template = folium.branca.element.Template(legend_html)
        
        # Add the feature group to the map
        fg.add_to(self.map)
        
        # Store layer reference
        self.layers.append({"name": name, "group": fg})
        
        return self.map
    
    def add_wind_layer(self, wind_data, name="Wind Patterns", palette="urban"):
        """
        Add wind pattern visualization using animated flow lines
        
        Args:
            wind_data: List of (lat, lon, u, v, speed) where u,v are vector components
            name: Layer name
            palette: Color palette from FELT_PALETTES
        """
        if not wind_data:
            print("No wind data provided")
            return self.map
        
        # Get palette colors
        if palette in FELT_PALETTES:
            colors = FELT_PALETTES[palette]["colors"]
        else:
            colors = FELT_PALETTES["urban"]["colors"]
        
        # Create feature group for the layer
        fg = folium.FeatureGroup(name=name)
        
        # Extract wind speeds for scaling
        speeds = [speed for _, _, _, _, speed in wind_data]
        min_speed = min(speeds)
        max_speed = max(speeds)
        
        # Create a color map for wind speed
        color_map = bcm.LinearColormap(
            colors=colors,
            vmin=min_speed,
            vmax=max_speed,
            caption='Wind Speed (m/s)'
        )
        
        # Add the color map to the map
        color_map.add_to(self.map)
        
        # Prepare wind vector data for animation
        features = []
        
        for lat, lon, u, v, speed in wind_data:
            # Skip points with no wind
            if speed <= 0:
                continue
            
            # Calculate normalized speed for color
            norm_speed = (speed - min_speed) / (max_speed - min_speed) if max_speed > min_speed else 0.5
            color_idx = min(len(colors) - 1, int(norm_speed * (len(colors) - 1)))
            color = colors[color_idx]
            
            # Calculate endpoint based on u,v components (scaled for visibility)
            scale_factor = 0.02  # Scale factor for vector length
            end_lon = lon + u * scale_factor
            end_lat = lat + v * scale_factor
            
            # Add line feature
            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [[lon, lat], [end_lon, end_lat]]
                },
                "properties": {
                    "times": ["2023-01-01T00:00:00Z", "2023-01-01T00:00:10Z"],
                    "speed": speed,
                    "style": {
                        "color": color,
                        "weight": min(5, max(1, speed / max_speed * 4)),
                        "opacity": 0.8
                    },
                    "icon": "circle",
                    "iconstyle": {
                        "fillColor": color,
                        "fillOpacity": 0.8,
                        "stroke": "true",
                        "radius": min(8, max(3, speed / max_speed * 6))
                    },
                    "popup": f"Wind Speed: {speed:.1f} m/s<br>Direction: {np.arctan2(v, u) * 180/np.pi:.1f}°"
                }
            })
        
        # Add animated wind vectors
        TimestampedGeoJson({
            "type": "FeatureCollection",
            "features": features
        }, period="PT10S", add_last_point=True, auto_play=True, loop=True).add_to(fg)
        
        # Add the feature group to the map
        fg.add_to(self.map)
        
        # Store layer reference
        self.layers.append({"name": name, "group": fg})
        
        return self.map
    
    def add_points_of_interest(self, poi_data, name="Points of Interest", cluster=True):
        """
        Add points of interest with custom markers
        
        Args:
            poi_data: List of (lat, lon, title, description, icon, color) tuples
            name: Layer name
            cluster: Whether to cluster nearby points
        """
        if not poi_data:
            print("No POI data provided")
            return self.map
        
        # Create feature group for the layer
        fg = folium.FeatureGroup(name=name)
        
        # Create marker cluster if requested
        if cluster:
            marker_cluster = MarkerCluster().add_to(fg)
        
        # Add each POI
        for lat, lon, title, description, icon, color in poi_data:
            # Default values
            if not icon:
                icon = "info-sign"
            if not color:
                color = "blue"
            
            # Create popup content
            popup_content = f"""
            <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                        max-width: 250px;">
                <h4 style="margin-bottom: 8px; color: #333;">{title}</h4>
                <p style="margin-top: 0; color: #555; font-size: 13px; line-height: 1.4;">
                    {description}
                </p>
            </div>
            """
            
            # Create marker
            marker = folium.Marker(
                location=[lat, lon],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=title,
                icon=folium.Icon(color=color, icon=icon, prefix='glyphicon')
            )
            
            # Add to cluster or directly to feature group
            if cluster:
                marker.add_to(marker_cluster)
            else:
                marker.add_to(fg)
        
        # Add the feature group to the map
        fg.add_to(self.map)
        
        # Store layer reference
        self.layers.append({"name": name, "group": fg})
        
        return self.map
    
    def add_custom_legend(self, title, items, position="bottomright"):
        """
        Add a custom legend to the map
        
        Args:
            title: Legend title
            items: List of (color, label) tuples
            position: Legend position
        """
        legend_html = f"""
        <div style="position: fixed; {position}; width: 180px; height: auto; 
                   background-color: white; border-radius: 5px; box-shadow: 0 0 15px rgba(0,0,0,0.1);
                   font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                   padding: 10px; font-size: 12px; z-index: 9999;">
            <div style="font-weight: bold; margin-bottom: 10px;">{title}</div>
        """
        
        for color, label in items:
            legend_html += f"""
            <div style="display: flex; align-items: center; margin-bottom: 5px;">
                <div style="background-color: {color}; width: 15px; height: 15px; 
                         border-radius: 3px; margin-right: 5px;"></div>
                <div>{label}</div>
            </div>
            """
        
        legend_html += "</div>"
        
        # Add the legend HTML as a macro element
        macro = folium.MacroElement().add_to(self.map)
        macro._template = folium.branca.element.Template(legend_html)
        
        return self.map
    
    def add_watermark(self, text="Climate Copilot", position="bottomleft"):
        """Add a subtle watermark to the map"""
        watermark_html = f"""
        <div style="position: fixed; {position}; margin: 10px; padding: 5px 10px;
                  background-color: rgba(255, 255, 255, 0.7); border-radius: 4px;
                  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                  font-size: 11px; color: #555; font-weight: 500; z-index: 900;">
            {text}
        </div>
        """
        
        # Add the watermark HTML as a macro element
        macro = folium.MacroElement().add_to(self.map)
        macro._template = folium.branca.element.Template(watermark_html)
        
        return self.map
    
    def get_map(self):
        """Return the Folium map object"""
        return self.map
    
    def render_in_streamlit(self):
        """Render the map in a Streamlit app"""
        import streamlit as st
        from streamlit_folium import folium_static
        
        folium_static(self.map, width=self.width, height=self.height)


def create_felt_inspired_map(lat, lon, zoom=10, width="100%", height=600, 
                            tiles="light", style="modern", show_toolbar=True, 
                            include_contours=True, contour_color="#6644aa"):
    """
    Create a Felt-inspired map for Climate Copilot
    
    Args:
        lat: Latitude
        lon: Longitude
        zoom: Zoom level
        width: Map width
        height: Map height
        tiles: Map tile source
        style: UI style
        show_toolbar: Whether to show the toolbar
        include_contours: Whether to include elevation contours
        contour_color: Color for contour lines
        
    Returns:
        FeltMap object
    """
    # Create the map
    felt_map = FeltMap(
        lat=lat,
        lon=lon,
        zoom=zoom,
        width=width,
        height=height,
        tiles=tiles,
        style=style,
        show_toolbar=show_toolbar
    )
    
    # Add elevation contours if requested
    if include_contours:
        felt_map.add_elevation_contours(color=contour_color)
        
    # Add watermark
    felt_map.add_watermark()
    
    return felt_map


def render_felt_map_in_streamlit(map_object):
    """Render a FeltMap object in Streamlit"""
    map_object.render_in_streamlit()


# Example code for testing the module (runs when the file is executed directly)
if __name__ == "__main__":
    # Create a map centered on San Francisco
    map = create_felt_inspired_map(
        lat=37.7749, 
        lon=-122.4194,
        zoom=12,
        tiles="outdoors",
        style="modern",
        include_contours=True
    )
    
    # Sample temperature data
    temp_data = [
        (37.78, -122.41, 15.5),
        (37.77, -122.43, 16.2),
        (37.75, -122.42, 17.8),
        (37.76, -122.40, 16.5)
    ]
    
    # Add temperature layer
    map.add_temperature_layer(temp_data, name="Temperature")
    
    # Save the map to an HTML file
    map.get_map().save("felt_example_map.html")
    
    print("Map created and saved to felt_example_map.html")