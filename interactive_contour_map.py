"""
Interactive Contour Map Module

This module creates an interactive map with Google Maps base that allows users to:
1. Draw polygons around areas of interest
2. Generate terrain contours at 1m, 5m, and 10m increments for selected areas
3. Display elevation data with high precision
"""

import streamlit as st
import folium
from folium.plugins import Draw
import geopandas as gpd
from shapely.geometry import Polygon, Point
import numpy as np
import requests
import json
import time
from typing import List, Tuple, Dict, Optional
import elevation
import rasterio
from rasterio.features import shapes
from rasterio.transform import from_bounds
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.patches import Polygon as MPLPolygon
import tempfile
import os

class InteractiveContourMap:
    """Interactive map with polygon selection and contour generation"""
    
    def __init__(self):
        self.map_center = [40.7128, -74.0060]  # Default to NYC
        self.zoom_level = 12
        self.elevation_cache = {}
        
    def create_base_map(self, center: List[float] = None, zoom: int = 12) -> folium.Map:
        """
        Create a base map with Google Maps tiles and drawing tools
        
        Args:
            center: Map center coordinates [lat, lon]
            zoom: Initial zoom level
            
        Returns:
            Folium map object
        """
        if center is None:
            center = self.map_center
            
        # Create map with Google Maps satellite tiles
        m = folium.Map(
            location=center,
            zoom_start=zoom,
            tiles=None
        )
        
        # Add Google Maps satellite tiles
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Satellite',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Add Google Maps terrain tiles as option
        folium.TileLayer(
            tiles='https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
            attr='Google',
            name='Google Terrain',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Add OpenStreetMap as backup
        folium.TileLayer(
            tiles='OpenStreetMap',
            name='OpenStreetMap',
            overlay=False,
            control=True
        ).add_to(m)
        
        # Add drawing tools
        draw = Draw(
            export=True,
            filename='polygon_data.geojson',
            position='topleft',
            draw_options={
                'polyline': False,
                'rectangle': True,
                'polygon': True,
                'circle': False,
                'marker': False,
                'circlemarker': False,
            },
            edit_options={'edit': True}
        )
        draw.add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        return m
    
    def get_elevation_data(self, polygon_coords: List[Tuple[float, float]], 
                          resolution: float = 1.0) -> Tuple[Optional[np.ndarray], Optional[object]]:
        """
        Get elevation data for a polygon area using Open-Elevation API
        
        Args:
            polygon_coords: List of (lat, lon) coordinates defining the polygon
            resolution: Resolution in arc-seconds for elevation data
            
        Returns:
            Tuple of elevation array and transform, or (None, None) if unavailable
        """
        try:
            # Create bounding box from polygon
            lats, lons = zip(*polygon_coords)
            min_lat, max_lat = min(lats), max(lats)
            min_lon, max_lon = min(lons), max(lons)
            
            # Create a grid of points within the polygon
            grid_resolution = 50  # Number of points per side
            lat_range = np.linspace(min_lat, max_lat, grid_resolution)
            lon_range = np.linspace(min_lon, max_lon, grid_resolution)
            
            elevation_data = np.zeros((grid_resolution, grid_resolution))
            
            # Use Open-Elevation API for authentic elevation data
            points = []
            for i, lat in enumerate(lat_range):
                for j, lon in enumerate(lon_range):
                    points.append(f"{lat},{lon}")
            
            # Split into smaller batches for API requests
            batch_size = 100
            data_retrieved = False
            
            for batch_start in range(0, len(points), batch_size):
                batch_points = points[batch_start:batch_start + batch_size]
                
                try:
                    # Open-Elevation API request
                    locations = "|".join(batch_points)
                    url = f"https://api.open-elevation.com/api/v1/lookup?locations={locations}"
                    
                    response = requests.get(url, timeout=30)
                    if response.status_code == 200:
                        data = response.json()
                        
                        for idx, result in enumerate(data['results']):
                            global_idx = batch_start + idx
                            i = global_idx // grid_resolution
                            j = global_idx % grid_resolution
                            if i < grid_resolution and j < grid_resolution:
                                elevation_data[i, j] = result['elevation']
                                data_retrieved = True
                    else:
                        st.warning(f"Elevation API returned status {response.status_code}")
                        
                except requests.RequestException as e:
                    st.warning(f"Could not fetch elevation data from API: {e}")
                    continue
                
                # Add delay to respect API limits
                time.sleep(0.1)
            
            if data_retrieved:
                # Create transform for coordinate mapping
                transform = from_bounds(min_lon, min_lat, max_lon, max_lat, 
                                      grid_resolution, grid_resolution)
                return elevation_data, transform
            else:
                st.error("No elevation data could be retrieved from external sources. Please check your internet connection or try a different area.")
                return None, None
            
        except Exception as e:
            st.error(f"Error accessing elevation data: {e}")
            return None, None
    
    def _estimate_terrain_elevation(self, polygon_coords: List[Tuple[float, float]], 
                                   grid_size: int = 50) -> Tuple[np.ndarray, object]:
        """
        Estimate terrain elevation based on geographic location and topographic patterns
        
        Args:
            polygon_coords: List of (lat, lon) coordinates
            grid_size: Size of the elevation grid
            
        Returns:
            Tuple of elevation array and transform
        """
        lats, lons = zip(*polygon_coords)
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        center_lat, center_lon = np.mean([min_lat, max_lat]), np.mean([min_lon, max_lon])
        
        # Create elevation grid based on geographic patterns
        lat_range = np.linspace(min_lat, max_lat, grid_size)
        lon_range = np.linspace(min_lon, max_lon, grid_size)
        elevation_data = np.zeros((grid_size, grid_size))
        
        for i, lat in enumerate(lat_range):
            for j, lon in enumerate(lon_range):
                # Base elevation from latitude (higher latitudes tend to be higher)
                base_elevation = max(0, abs(lat) * 10 - 200)
                
                # Add coastal effects (lower near water)
                coastal_factor = 1.0
                if abs(lat) < 45:  # Tropical/temperate zones
                    coastal_factor = 0.7
                
                # Add distance-based variation
                distance_from_center = np.sqrt((lat - center_lat)**2 + (lon - center_lon)**2)
                elevation_variation = 100 * np.sin(distance_from_center * 500) * np.cos(distance_from_center * 300)
                
                # Add random terrain features
                terrain_noise = np.random.normal(0, 20)
                
                final_elevation = max(0, (base_elevation + elevation_variation + terrain_noise) * coastal_factor)
                elevation_data[i, j] = final_elevation
        
        # Smooth the data for more realistic terrain
        from scipy.ndimage import gaussian_filter
        elevation_data = gaussian_filter(elevation_data, sigma=1.5)
        
        # Create transform
        transform = from_bounds(min_lon, min_lat, max_lon, max_lat, grid_size, grid_size)
        
        return elevation_data, transform
    
    def generate_contours(self, elevation_data: np.ndarray, transform: object,
                         intervals: List[int] = [1, 5, 10]) -> Dict[str, List]:
        """
        Generate contour lines from elevation data
        
        Args:
            elevation_data: 2D numpy array of elevation values
            transform: Rasterio transform object
            intervals: List of contour intervals in meters
            
        Returns:
            Dictionary with contour data for each interval
        """
        contours = {}
        
        try:
            for interval in intervals:
                # Calculate contour levels
                min_elev = np.nanmin(elevation_data)
                max_elev = np.nanmax(elevation_data)
                levels = np.arange(
                    int(min_elev // interval) * interval,
                    int(max_elev // interval + 1) * interval,
                    interval
                )
                
                # Generate contours using matplotlib
                fig, ax = plt.subplots(figsize=(10, 10))
                
                # Create coordinate arrays
                height, width = elevation_data.shape
                x = np.linspace(0, width, width)
                y = np.linspace(0, height, height)
                X, Y = np.meshgrid(x, y)
                
                # Generate contour lines
                contour_set = ax.contour(X, Y, elevation_data, levels=levels)
                
                # Extract contour paths
                contour_lines = []
                for i, collection in enumerate(contour_set.collections):
                    elevation_level = levels[i] if i < len(levels) else levels[-1]
                    
                    for path in collection.get_paths():
                        vertices = path.vertices
                        if len(vertices) > 2:  # Only include valid contours
                            # Transform pixel coordinates to geographic coordinates
                            geo_coords = []
                            for vertex in vertices:
                                lon, lat = rasterio.transform.xy(transform, vertex[1], vertex[0])
                                geo_coords.append([lat, lon])
                            
                            contour_lines.append({
                                'coordinates': geo_coords,
                                'elevation': elevation_level
                            })
                
                contours[f"{interval}m"] = contour_lines
                plt.close(fig)
                
        except Exception as e:
            st.error(f"Error generating contours: {e}")
            contours = {f"{interval}m": [] for interval in intervals}
        
        return contours
    
    def add_contours_to_map(self, map_obj: folium.Map, contours: Dict[str, List],
                           polygon_coords: List[Tuple[float, float]]) -> folium.Map:
        """
        Add contour lines to the map
        
        Args:
            map_obj: Folium map object
            contours: Dictionary with contour data
            polygon_coords: Original polygon coordinates
            
        Returns:
            Updated folium map
        """
        # Define colors for different intervals
        colors = {
            '1m': '#8B4513',   # Brown for 1m contours
            '5m': '#FF6347',   # Tomato for 5m contours  
            '10m': '#FF0000'   # Red for 10m contours
        }
        
        weights = {
            '1m': 1,
            '5m': 2,
            '10m': 3
        }
        
        # Create feature groups for each contour interval
        for interval, contour_lines in contours.items():
            feature_group = folium.FeatureGroup(name=f"Contours {interval}")
            
            for line_data in contour_lines:
                coordinates = line_data['coordinates']
                elevation = line_data['elevation']
                
                if len(coordinates) > 1:
                    folium.PolyLine(
                        locations=coordinates,
                        color=colors.get(interval, '#000000'),
                        weight=weights.get(interval, 1),
                        opacity=0.8,
                        popup=f"Elevation: {elevation:.1f}m"
                    ).add_to(feature_group)
            
            feature_group.add_to(map_obj)
        
        # Add the original polygon outline
        if polygon_coords:
            folium.Polygon(
                locations=polygon_coords,
                color='blue',
                weight=3,
                fill=False,
                opacity=0.8,
                popup="Selected Area"
            ).add_to(map_obj)
        
        return map_obj
    
    def display_elevation_stats(self, elevation_data: np.ndarray):
        """
        Display elevation statistics
        
        Args:
            elevation_data: 2D numpy array of elevation values
        """
        if elevation_data is not None and elevation_data.size > 0:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Min Elevation", f"{np.nanmin(elevation_data):.1f}m")
            
            with col2:
                st.metric("Max Elevation", f"{np.nanmax(elevation_data):.1f}m")
            
            with col3:
                st.metric("Mean Elevation", f"{np.nanmean(elevation_data):.1f}m")
            
            with col4:
                st.metric("Elevation Range", f"{np.nanmax(elevation_data) - np.nanmin(elevation_data):.1f}m")


def display_interactive_contour_map():
    """
    Main function to display the interactive contour map interface
    """
    st.markdown("""
    <div style="background: linear-gradient(90deg, #1E90FF, #9370DB); 
              -webkit-background-clip: text;
              -webkit-text-fill-color: transparent;
              font-weight: bold;
              font-size: 24px;
              margin-bottom: 20px;">
        Interactive Terrain Contour Map
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **Instructions:**
    1. Use the drawing tools on the left side of the map to draw a polygon around your area of interest
    2. Click "Generate Contours" to create elevation contours at 1m, 5m, and 10m intervals
    3. Toggle different contour layers using the layer control on the map
    """)
    
    # Initialize the map
    contour_map = InteractiveContourMap()
    
    # Location input
    col1, col2 = st.columns(2)
    with col1:
        center_lat = st.number_input("Center Latitude", value=40.7128, format="%.6f")
    with col2:
        center_lon = st.number_input("Center Longitude", value=-74.0060, format="%.6f")
    
    # Contour intervals
    st.subheader("Contour Settings")
    col1, col2, col3 = st.columns(3)
    with col1:
        enable_1m = st.checkbox("1m Contours", value=True)
    with col2:
        enable_5m = st.checkbox("5m Contours", value=True)
    with col3:
        enable_10m = st.checkbox("10m Contours", value=True)
    
    intervals = []
    if enable_1m:
        intervals.append(1)
    if enable_5m:
        intervals.append(5)
    if enable_10m:
        intervals.append(10)
    
    # Create the base map
    m = contour_map.create_base_map(center=[center_lat, center_lon])
    
    # Polygon input section
    st.subheader("Polygon Definition")
    
    # Option to manually input polygon coordinates
    manual_input = st.checkbox("Manually input polygon coordinates")
    
    polygon_coords = None
    
    if manual_input:
        coord_text = st.text_area(
            "Enter polygon coordinates (lat,lon pairs, one per line):",
            value="40.7128,-74.0060\n40.7138,-74.0050\n40.7148,-74.0070\n40.7128,-74.0080"
        )
        
        if coord_text:
            try:
                coords = []
                for line in coord_text.strip().split('\n'):
                    if ',' in line:
                        lat, lon = map(float, line.split(','))
                        coords.append([lat, lon])
                
                if len(coords) >= 3:
                    polygon_coords = coords
                    # Add polygon to map
                    folium.Polygon(
                        locations=polygon_coords,
                        color='blue',
                        weight=3,
                        fill=True,
                        fillOpacity=0.2,
                        popup="Manual Polygon"
                    ).add_to(m)
                else:
                    st.warning("Please enter at least 3 coordinate pairs")
                    
            except ValueError:
                st.error("Invalid coordinate format. Use: lat,lon")
    
    # Generate contours button
    if st.button("Generate Contours", type="primary"):
        if polygon_coords and len(polygon_coords) >= 3:
            with st.spinner("Generating elevation contours..."):
                # Get elevation data
                elevation_data, transform = contour_map.get_elevation_data(polygon_coords)
                
                if elevation_data is not None:
                    # Display elevation statistics
                    contour_map.display_elevation_stats(elevation_data)
                    
                    # Generate contours
                    contours = contour_map.generate_contours(elevation_data, transform, intervals)
                    
                    # Add contours to map
                    m = contour_map.add_contours_to_map(m, contours, polygon_coords)
                    
                    st.success(f"Generated contours for {len(intervals)} interval(s)")
                else:
                    st.error("Could not retrieve elevation data for this area")
        else:
            st.warning("Please draw a polygon on the map or enter manual coordinates first")
    
    # Display the map
    st.subheader("Interactive Map")
    
    # Map display with streamlit_folium
    from streamlit_folium import st_folium
    st_folium(m, height=600, width=700)
    
    # Information section
    st.subheader("Map Features")
    st.markdown("""
    - **Google Satellite**: High-resolution satellite imagery
    - **Google Terrain**: Terrain visualization with roads and labels
    - **OpenStreetMap**: Standard map view as backup
    - **Drawing Tools**: Rectangle and polygon drawing tools
    - **Contour Lines**: 
        - Brown lines: 1m elevation intervals
        - Orange lines: 5m elevation intervals  
        - Red lines: 10m elevation intervals
    """)


if __name__ == "__main__":
    display_interactive_contour_map()