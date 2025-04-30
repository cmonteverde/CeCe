"""
SRTM Elevation Data Module

This module provides functions to access NASA SRTM elevation data 
using direct HTTP access to AWS public dataset.

The Shuttle Radar Topography Mission (SRTM) provides elevation data 
for Earth land surfaces between latitudes 60° north and 56° south.
"""

import os
import io
import tempfile
import requests
import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import calculate_default_transform, reproject, Resampling
import matplotlib.pyplot as plt

# NASA SRTM V3 data is available as AWS Public Dataset
# Documentation: https://registry.opendata.aws/terrain-tiles/
# SRTM tiles are 1 degree by 1 degree
# Tile naming follows the pattern: N00E072.hgt (North 00, East 072)

# Constants for SRTM data
SRTM_TILE_SIZE = 3601  # 3601 x 3601 cells for SRTM1 (1 arc-second resolution)
SRTM_NODATA = -32768  # SRTM No Data value
SRTM_BASE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/skadi"

def get_tile_indices(lat, lon):
    """Get SRTM tile indices for a given latitude and longitude"""
    lat_index = int(lat)
    lon_index = int(lon)
    return lat_index, lon_index

def get_tile_name(lat_index, lon_index):
    """Construct SRTM tile name from indices"""
    ns = 'N' if lat_index >= 0 else 'S'
    ew = 'E' if lon_index >= 0 else 'W'
    
    # Ensure positive values and two-digit formatting
    lat_str = f"{abs(lat_index):02d}"
    lon_str = f"{abs(lon_index):03d}"
    
    return f"{ns}{lat_str}{ew}{lon_str}"

def download_srtm_tile(lat_index, lon_index):
    """Download SRTM tile for given indices"""
    # SRTM data is only available between latitudes 60°N and 56°S
    if lat_index > 60 or lat_index < -56:
        print(f"SRTM data is not available for latitude {lat_index} (outside 60°N to 56°S range)")
        return None
    
    tile_name = get_tile_name(lat_index, lon_index)
    
    # Construct URL path - folders are named by latitude bands (N01, S08, etc.)
    lat_band = 'N' if lat_index >= 0 else 'S'
    lat_band += f"{abs(lat_index):02d}"
    
    url = f"{SRTM_BASE_URL}/{lat_band}/{tile_name}.hgt.gz"
    print(f"Downloading SRTM tile from: {url}")
    
    # We'll try several sources for the data
    sources = [
        f"{SRTM_BASE_URL}/{lat_band}/{tile_name}.hgt.gz",  # AWS open data
        f"https://srtm.csi.cgiar.org/wp-content/uploads/files/srtm_5x5/TIFF/{tile_name}.zip",  # CGIAR mirror
    ]
    
    # Try each source in order
    for url in sources:
        # Create temp file for downloaded data
        with tempfile.NamedTemporaryFile(delete=False, suffix='.hgt.gz') as tmp_file:
            try:
                print(f"Attempting download from: {url}")
                response = requests.get(url, stream=True)
                
                if response.status_code == 200:
                    # Check if we got a valid response (not an HTML error page)
                    content_type = response.headers.get('Content-Type', '')
                    if 'text/html' in content_type or 'text/xml' in content_type:
                        print(f"Received HTML/XML content instead of binary data")
                        continue
                    
                    # Check the file size - SRTM tiles should be quite large
                    if 'Content-Length' in response.headers:
                        content_length = int(response.headers['Content-Length'])
                        if content_length < 100000:  # Less than 100 KB is probably an error
                            print(f"File too small ({content_length} bytes), likely not valid SRTM data")
                            continue
                    
                    # Write the data to the temp file
                    for chunk in response.iter_content(chunk_size=8192):
                        tmp_file.write(chunk)
                    
                    tmp_file.flush()
                    
                    # Verify that we got a gzipped file
                    import gzip
                    try:
                        with gzip.open(tmp_file.name, 'rb') as test:
                            # Try reading the first few bytes to check if it's a valid gzip file
                            test.read(100)
                        return tmp_file.name
                    except Exception as e:
                        print(f"Downloaded file is not a valid gzip file: {e}")
                        continue
                else:
                    print(f"Failed to download from {url}: HTTP status {response.status_code}")
            except Exception as e:
                print(f"Error downloading SRTM data from {url}: {e}")
    
    print("Could not download SRTM data from any source")
    return None

def read_srtm_data(file_path, bounds=None):
    """
    Read SRTM data from file and extract region defined by bounds
    
    Args:
        file_path: Path to SRTM tile file (.hgt.gz)
        bounds: Optional tuple (minx, miny, maxx, maxy) in geographic coordinates
        
    Returns:
        Tuple of (elevation_array, transform, extent)
    """
    try:
        import gzip
        import struct
        import subprocess
        import tempfile
        
        # First, gunzip the file to a temporary location
        temp_hgt = tempfile.NamedTemporaryFile(delete=False, suffix='.hgt')
        temp_hgt.close()
        
        try:
            # Use subprocess to gunzip the file
            subprocess.run(['gunzip', '-c', file_path], stdout=open(temp_hgt.name, 'wb'), check=True)
            
            # Get the original file name for coordinates
            filename = os.path.basename(file_path)
            if filename.endswith('.gz'):
                filename = filename[:-3]  # Remove .gz
                
            # Open the unzipped file
            with open(temp_hgt.name, 'rb') as hgt_file:
                # SRTM tiles are 3601x3601 16-bit signed integers in big-endian format
                # Read raw binary data directly without header assumptions
                raw_data = hgt_file.read()
                
                # Check if the file size is correct
                expected_size = SRTM_TILE_SIZE * SRTM_TILE_SIZE * 2  # 2 bytes per elevation value
                if len(raw_data) != expected_size:
                    raise ValueError(f"Unexpected file size: {len(raw_data)} bytes, expected {expected_size} bytes")
                
                # Format the data into a numpy array
                elevation_data = np.frombuffer(raw_data, dtype='>i2').reshape((SRTM_TILE_SIZE, SRTM_TILE_SIZE))
                
                # Replace No Data values
                elevation_data = elevation_data.astype(np.float32)
                elevation_data[elevation_data == SRTM_NODATA] = np.nan
                
                # Extract lat/lon from filename - assuming format like N48E002.hgt
                parts = os.path.basename(filename).split('.')[0]  # Remove file extension
                
                # Extract coordinates
                lat_dir = parts[0]
                lat_val = int(parts[1:3])
                lon_dir = parts[3]
                lon_val = int(parts[4:7])
                
                # Adjust for S and W
                if lat_dir == 'S':
                    lat_val = -lat_val
                if lon_dir == 'W':
                    lon_val = -lon_val
                
                # The tile covers lat to lat+1, lon to lon+1
                # But we need the northwest corner for the origin
                north = lat_val + 1
                west = lon_val
                
                # Calculate pixel size (degrees) 
                pixel_size = 1.0 / (SRTM_TILE_SIZE - 1)
                
                # Create transform
                transform = from_origin(west, north, pixel_size, pixel_size)
                
                # If bounds are specified, extract the relevant portion
                if bounds:
                    minx, miny, maxx, maxy = bounds
                    
                    # Convert bounds to pixel coordinates
                    row_min, col_min = ~transform * (minx, maxy)
                    row_max, col_max = ~transform * (maxx, miny)
                    
                    # Convert to integers and ensure they're within tile bounds
                    row_min = max(0, min(SRTM_TILE_SIZE-1, int(row_min)))
                    row_max = max(0, min(SRTM_TILE_SIZE-1, int(row_max)))
                    col_min = max(0, min(SRTM_TILE_SIZE-1, int(col_min)))
                    col_max = max(0, min(SRTM_TILE_SIZE-1, int(col_max)))
                    
                    # Extract the subset of data
                    subset = elevation_data[row_min:row_max+1, col_min:col_max+1]
                    
                    # Calculate new transform for the subset
                    new_west = west + col_min * pixel_size
                    new_north = north - row_min * pixel_size
                    new_transform = from_origin(new_west, new_north, pixel_size, pixel_size)
                    
                    # Calculate extent for visualization
                    extent = (new_west, new_west + subset.shape[1] * pixel_size,
                            new_north - subset.shape[0] * pixel_size, new_north)
                    
                    return subset, new_transform, extent
                else:
                    # Return full tile
                    extent = (west, west + elevation_data.shape[1] * pixel_size,
                            north - elevation_data.shape[0] * pixel_size, north)
                    return elevation_data, transform, extent
        finally:
            # Clean up temporary file
            try:
                os.unlink(temp_hgt.name)
            except:
                pass
                
    except Exception as e:
        print(f"Error reading SRTM data: {e}")
        return None, None, None

def fetch_elevation_from_api(lat, lon, width=100, height=100, radius=0.05):
    """
    Fetch elevation data from OpenTopoData API for a region centered at lat, lon
    
    Args:
        lat: Center latitude
        lon: Center longitude
        width: Width of output array
        height: Height of output array
        radius: Radius around center point in degrees
    
    Returns:
        Tuple of (elevation_array, bounds)
    """
    try:
        print(f"Fetching elevation data from API for {lat}, {lon} with radius {radius} degrees")
        
        # Calculate bounds from center and radius
        minx = lon - radius
        maxx = lon + radius
        miny = lat - radius
        maxy = lat + radius
        bounds = (minx, miny, maxx, maxy)
        
        # Create a grid of points
        lats = np.linspace(miny, maxy, height)
        lons = np.linspace(minx, maxx, width)
        
        # OpenTopoData API has a limit on the number of points per request (usually 100-1000)
        max_points_per_request = 100
        
        # Prepare to collect all elevation data
        elevation_data = np.zeros((height, width), dtype=np.float32)
        
        # Process the grid in chunks
        total_requests = 0
        max_requests = 20  # Limit the number of requests to avoid overwhelming the API
        
        for i in range(0, height, 10):
            if total_requests >= max_requests:
                print(f"Reached maximum number of API requests ({max_requests})")
                break
                
            i_end = min(i + 10, height)
            for j in range(0, width, 10):
                if total_requests >= max_requests:
                    break
                    
                j_end = min(j + 10, width)
                
                # Create a list of point coordinates for this chunk
                points = []
                for lat_idx in range(i, i_end):
                    for lon_idx in range(j, j_end):
                        points.append((lats[lat_idx], lons[lon_idx]))
                
                # Make API request for this chunk of points
                points_str = "|".join([f"{lat},{lon}" for lat, lon in points])
                api_url = f"https://api.opentopodata.org/v1/srtm30m?locations={points_str}"
                
                try:
                    print(f"API request: {api_url[:60]}...")
                    response = requests.get(api_url)
                    total_requests += 1
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "results" in data and len(data["results"]) > 0:
                            # Fill the elevation grid with the results
                            point_idx = 0
                            for lat_idx in range(i, i_end):
                                for lon_idx in range(j, j_end):
                                    if point_idx < len(data["results"]):
                                        elevation_data[lat_idx, lon_idx] = data["results"][point_idx]["elevation"]
                                    point_idx += 1
                    else:
                        print(f"API error: {response.status_code}")
                        # Continue to next chunk
                except Exception as e:
                    print(f"API request error: {e}")
                    # Continue to next chunk
        
        # If we got elevation data (not all zeros), return it
        if np.any(elevation_data):
            print("Successfully fetched elevation data from API")
            return elevation_data, bounds
        else:
            print("No elevation data retrieved from API")
            return None, bounds
    except Exception as e:
        print(f"Error fetching elevation data from API: {e}")
        return None, (lon-radius, lat-radius, lon+radius, lat+radius)

def fetch_elevation_array(lat, lon, width=100, height=100, radius=0.05):
    """
    Fetch elevation data for a region centered at lat, lon
    
    Args:
        lat: Center latitude
        lon: Center longitude
        width: Width of output array
        height: Height of output array
        radius: Radius around center point in degrees
    
    Returns:
        Tuple of (elevation_array, bounds)
    """
    # Try OpenTopoData API first - this is often more reliable
    elevation_data, bounds = fetch_elevation_from_api(lat, lon, width, height, radius)
    if elevation_data is not None:
        return elevation_data, bounds
    
    # If API failed, try downloading the SRTM tile directly
    try:
        # Calculate bounds from center and radius
        minx = lon - radius
        maxx = lon + radius
        miny = lat - radius
        maxy = lat + radius
        bounds = (minx, miny, maxx, maxy)
        
        # Get tile indices for center point
        lat_index, lon_index = get_tile_indices(lat, lon)
        
        # Download tile
        tile_file = download_srtm_tile(lat_index, lon_index)
        if tile_file is None:
            print(f"No SRTM data available for coordinates: {lat}, {lon}")
            return None, bounds
        
        # Read data
        elevation_data, transform, extent = read_srtm_data(tile_file, bounds)
        
        # Clean up temporary file
        try:
            os.unlink(tile_file)
        except:
            pass
        
        if elevation_data is None:
            print(f"Could not read elevation data for coordinates: {lat}, {lon}")
            return None, bounds
        
        # Resample to desired dimensions if necessary
        if elevation_data.shape != (height, width):
            # Create a regular grid with desired dimensions
            resampled = np.zeros((height, width), dtype=np.float32)
            
            # Simple resampling by interpolation
            y_old = np.linspace(0, 1, elevation_data.shape[0])
            x_old = np.linspace(0, 1, elevation_data.shape[1])
            y_new = np.linspace(0, 1, height)
            x_new = np.linspace(0, 1, width)
            
            from scipy.interpolate import RegularGridInterpolator
            
            # Handle NaN values
            mask = np.isnan(elevation_data)
            if np.all(mask):
                print("All elevation values are NaN!")
                return None, bounds
            
            # Fill NaN with mean of valid values
            elevation_data_filled = elevation_data.copy()
            elevation_data_filled[mask] = np.nanmean(elevation_data)
            
            # Create interpolator
            interpolator = RegularGridInterpolator((y_old, x_old), elevation_data_filled,
                                                 method='linear', bounds_error=False,
                                                 fill_value=np.nanmean(elevation_data))
            
            # Create meshgrid for new coordinates
            ynew, xnew = np.meshgrid(y_new, x_new, indexing='ij')
            pts = np.column_stack([ynew.flatten(), xnew.flatten()])
            
            # Interpolate
            resampled = interpolator(pts).reshape(height, width)
            
            return resampled, bounds
        
        return elevation_data, bounds
        
    except Exception as e:
        print(f"Error fetching elevation data: {e}")
        return None, (lon-radius, lat-radius, lon+radius, lat+radius)

def generate_synthetic_elevation(width, height, bounds=None):
    """
    Generate synthetic elevation data for testing or when SRTM data is unavailable
    
    Args:
        width: Grid width
        height: Grid height
        bounds: Optional bounds (min_lon, min_lat, max_lon, max_lat)
    
    Returns:
        Numpy array with synthetic elevation data
    """
    # Create base elevation
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    X, Y = np.meshgrid(x, y)
    
    # Create a mountain with multiple peaks
    elevation = (
        500 * np.exp(-((X - 0.3)**2 + (Y - 0.3)**2) / 0.1) + 
        800 * np.exp(-((X - 0.7)**2 + (Y - 0.7)**2) / 0.1) +
        300 * np.exp(-((X - 0.5)**2 + (Y - 0.1)**2) / 0.1) +
        200 * np.sin(X * 10) * np.cos(Y * 8)
    )
    
    # Add some noise for realism
    elevation += np.random.normal(0, 50, (height, width))
    
    # Calculate bounds if not provided
    if bounds is None:
        # Use a default area (around San Francisco for demonstration)
        bounds = (-122.5, 37.7, -122.4, 37.8)
    
    # Log that we're using synthetic data
    print(f"Using synthetic elevation data for area: {bounds}")
    
    return elevation

if __name__ == "__main__":
    # Test code
    lat, lon = 37.7749, -122.4194  # San Francisco
    elevation_data, bounds = fetch_elevation_array(lat, lon, width=100, height=100, radius=0.05)
    
    if elevation_data is not None:
        plt.figure(figsize=(10, 8))
        plt.imshow(elevation_data, cmap='terrain')
        plt.colorbar(label='Elevation (meters)')
        plt.title(f"SRTM Elevation Data for {lat}, {lon}")
        plt.show()